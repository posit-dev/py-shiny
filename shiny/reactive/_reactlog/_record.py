"""Record a real Shiny session in a browser (or wait for one) and fetch its reactlog."""

from __future__ import annotations

import importlib.util
import inspect
import json
import shutil
import signal
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Generator

from ...run._run import ShinyAppProc, run_shiny_app
from ._codegen import REDACTED

if TYPE_CHECKING:
    from playwright.sync_api import Browser, BrowserContext, Page, Video

_APP_ENV = {"SHINY_REACTLOG": "1", "SHINY_TESTMODE": "1", "PYTHONUNBUFFERED": "1"}

# Streams browser actions and session ids to Python as they happen, so closing the
# window or reloading the page loses nothing.
RECORDER_SCRIPT = "(() => {\n  const REDACTED = " + json.dumps(REDACTED) + ";" + r"""
  const send = (item) => {
    item.time = Date.now() / 1000;
    if (window.__shinyReactlogAction) window.__shinyReactlogAction(item);
  };
  const sensitive = (name, el) => {
    if (window.__shinyReactlogRedactAll) return true;
    if (el && (el.type === "password")) return true;
    const lower = (name || "").toLowerCase();
    return ["password", "secret", "token", "api_key", "apikey"].some((s) => lower.includes(s));
  };
  const attach = () => {
    if (!(window.$ && window.Shiny)) return;
    $(document).off(".shinyReactlog");
    $(document).on("shiny:sessioninitialized.shinyReactlog", () => {
      if (window.__shinyReactlogSession) {
        window.__shinyReactlogSession(Shiny.shinyapp.config.sessionId);
      }
    });
    $(document).on("shiny:inputchanged.shinyReactlog", (e) => {
      if (e.name.startsWith(".")) return;
      const el = e.el || document.getElementById(e.name);
      // Sliders: the formatted label text the Playwright controller drags until it matches.
      const box = el && el.closest ? el.closest(".shiny-input-container") : null;
      const txt = (sel) => {
        const n = box && box.querySelector(sel);
        return n ? n.textContent : null;
      };
      // Date inputs: the visible field text, which follows the input's `format`.
      const fields = () => (box ? Array.from(box.querySelectorAll("input"), (n) => n.value) : []);
      const binding = e.binding && e.binding.name ? e.binding.name : null;
      let display = null;
      if (!sensitive(e.name, el)) {
        if (binding === "shiny.sliderInput") {
          display = Array.isArray(e.value) ? [txt(".irs-from"), txt(".irs-to")] : txt(".irs-single");
        } else if (binding === "shiny.dateInput") {
          display = fields()[0] ?? null;
        } else if (binding === "shiny.dateRangeInput") {
          const [from, to] = fields();
          display = [from ?? null, to ?? null];
        }
      }
      send({
        type: "input",
        display: display,
        name: e.name,
        value: sensitive(e.name, el) ? REDACTED : e.value,
        inputType: e.inputType || "",
        binding: binding,
        tag: el ? el.tagName : "",
        elType: el && el.type ? String(el.type) : "",
        classes: el && el.className ? String(el.className) : "",
        container: el && el.closest && el.closest(".shiny-input-container")
          ? String(el.closest(".shiny-input-container").className) : "",
      });
    });
    $(document).on("shiny:value.shinyReactlog", (e) => {
      // Outputs arrive wrapped in an adapter; the named binding is inside it.
      const inner = e.binding && e.binding.binding ? e.binding.binding : e.binding;
      const binding = inner && inner.name ? inner.name : null;
      const el = document.getElementById(e.name);
      send({
        type: "output",
        name: e.name,
        binding: binding,
        tag: el ? el.tagName : "",
        value: binding === "shiny.textOutput" && typeof e.value === "string" ? e.value : undefined,
      });
    });
    // The server finished a flush. py-shiny sends this just before the flush's values.
    $(document).on("shiny:idle.shinyReactlog", () => send({ type: "idle" }));
  };
  document.addEventListener("DOMContentLoaded", attach);
  window.addEventListener("load", attach);
})();
"""


class RecordingError(Exception):
    """A recording could not be made; the message is shown to the user as-is."""


@dataclass
class Recording:
    export: dict[str, Any]
    actions: list[dict[str, Any]] = field(default_factory=list[dict[str, Any]])
    video_path: Path | None = None
    session_id: str = ""


def _start_app(app_file: Path) -> ShinyAppProc:
    try:
        # A terminal's Ctrl+C goes to the whole process group; in its own session
        # the app keeps running until the recording is exported.
        return run_shiny_app(
            app_file, wait_for_start=True, env=_APP_ENV, start_new_session=True
        )
    except Exception as err:  # run_shiny_app raises various errors for a bad app
        # The message ends with the app's stderr, whose last lines name the problem.
        text = str(err).partition("stderr:\n")[2] or str(err)
        tail = [line for line in text.splitlines() if line.strip()][-5:]
        raise RecordingError(
            "\n".join([f"Failed to start Shiny app {app_file}:", *tail])
        ) from err


@contextmanager
def _terminate_as_interrupt() -> Generator[None]:
    """
    Treat SIGTERM and SIGHUP like Ctrl+C while an app is running.

    The app runs in its own session, so it only stops through the callers' `finally`
    blocks, which these signals' default actions would skip.
    """
    if threading.current_thread() is not threading.main_thread():
        yield
        return

    def interrupt(signum: int, frame: object) -> None:
        raise KeyboardInterrupt

    names = ["SIGTERM", "SIGHUP"]  # SIGHUP does not exist on Windows
    previous = {
        sig: signal.signal(sig, interrupt)
        for sig in (getattr(signal, name) for name in names if hasattr(signal, name))
    }
    try:
        yield
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def _get_json(app: ShinyAppProc, path: str) -> Any:
    try:
        with urllib.request.urlopen(app.url + path, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    # HTTPError is a URLError subclass.
    except (urllib.error.URLError, json.JSONDecodeError) as err:
        if app.proc.poll() is not None:
            raise RecordingError(
                "The app stopped before the recording could be exported."
            ) from err
        raise RecordingError(
            f"Could not fetch the recorded reactlog from the app: {err}"
        ) from err


def _export(app: ShinyAppProc, session_id: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"session_id": session_id})
    return _get_json(app, f"__reactlog__/export?{query}")


def _start_stdin_reader(done: threading.Event) -> bool:
    """
    Set `done` when the user presses Enter; return whether a reader was started.

    Only reads from an interactive terminal: piped or closed stdin would hit EOF at
    once (ending the recording) or swallow input meant for a later prompt.
    """
    stdin = sys.stdin
    if stdin is None or not stdin.isatty():
        return False

    def read_stdin() -> None:
        if stdin.readline():  # "" is EOF, not Enter
            done.set()

    threading.Thread(target=read_stdin, daemon=True).start()
    return True


def redact_export(export: dict[str, Any]) -> None:
    """Replace every recorded input value in `export` with `REDACTED`, in place."""
    for entry in export["log"]:
        if entry.get("action") == "valueChange" and entry.get("type") == "input":
            entry["value"] = REDACTED


def _wait_for_enter_or_close(
    page: Page, timeout_secs: float, stop: threading.Event | None = None
) -> None:
    done = threading.Event()
    if _start_stdin_reader(done):
        sys.stderr.write(
            "Recording. Interact with the app, then press Enter here "
            "(or close the browser window) to finish.\n"
        )
    else:
        sys.stderr.write(
            "Recording. Interact with the app, then close the browser window "
            "to finish.\n"
        )
    deadline = time.time() + timeout_secs
    while (
        not done.is_set()
        and not (stop is not None and stop.is_set())
        and time.time() < deadline
        and not page.is_closed()
    ):
        try:
            # Also lets Playwright deliver exposed-function calls.
            page.wait_for_timeout(250)
        # The browser was quit, or Ctrl+C also stopped the Playwright driver (which
        # raises a plain Exception).
        except Exception:
            break


def _close_browser(
    page: Page,
    *,
    context: BrowserContext,
    browser: Browser,
    video: Video | None,
    video_path: Path | None,
) -> Path | None:
    """
    Close the browser, saving the video to `video_path`; return it if it was saved.

    Best effort: the user may have quit the browser, and a terminal's Ctrl+C also
    stops the Playwright driver, so any error here only loses the video, never the
    recording.
    """
    saved: Path | None = None
    try:
        if not page.is_closed():
            page.close()
        context.close()
        if video is not None and video_path is not None:
            video_path.parent.mkdir(parents=True, exist_ok=True)
            video.save_as(str(video_path))
            saved = video_path
        browser.close()
    except Exception as err:  # Playwright errors, a dead driver, or OSError
        if video_path is not None and saved is None:
            sys.stderr.write(f"Video could not be saved: {err}\n")
    return saved


def record_session(
    app_file: Path,
    *,
    video_path: Path | None,
    script: Callable[[Page, str], None] | None = None,
    redact_inputs: bool = False,
    timeout_secs: float = 3600.0,
) -> Recording:
    """
    Run `app_file` with reactlog on, record one browser session, and return its export.

    With `script`, the browser is headless and `script(page, app_url)` drives it (it
    must navigate itself); otherwise a headed browser opens and the user finishes with
    Enter or by closing the window.

    Raises
    ------
    RecordingError
        If Playwright is missing, the app fails to start, or no session started.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as err:
        raise RecordingError(
            "Playwright is not installed. Install it with: "
            "pip install playwright && playwright install chromium"
        ) from err

    app = _start_app(app_file)
    video_dir = Path(tempfile.mkdtemp(prefix="shiny_reactlog_"))
    stop = threading.Event()  # set on Ctrl+C: "finish", not "abort"
    actions: list[dict[str, Any]] = []
    session_ids: list[str] = []

    # Playwright can't register bound builtins like `list.append` directly.
    def on_action(item: dict[str, Any]) -> None:
        actions.append(item)

    def on_session(session_id: str) -> None:
        session_ids.append(session_id)

    def drive_browser() -> tuple[float, Path | None]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=script is not None)
            context = browser.new_context(
                viewport={"width": 1280, "height": 900},
                record_video_dir=str(video_dir) if video_path is not None else None,
                record_video_size={"width": 1280, "height": 900},
            )
            # Playwright types `callback` as a bare `Callable`.
            context.expose_function(  # pyright: ignore[reportUnknownMemberType]
                "__shinyReactlogAction", on_action
            )
            context.expose_function(  # pyright: ignore[reportUnknownMemberType]
                "__shinyReactlogSession", on_session
            )
            # One script, so the redaction flag is set before the recorder runs.
            redact_js = "true" if redact_inputs else "false"
            context.add_init_script(
                f"window.__shinyReactlogRedactAll = {redact_js};\n" + RECORDER_SCRIPT
            )
            page = context.new_page()
            video_start = time.time()
            video = page.video
            if script is not None:
                script(page, app.url)
            else:
                page.goto(app.url)
                _wait_for_enter_or_close(page, timeout_secs, stop)
            saved = _close_browser(
                page,
                context=context,
                browser=browser,
                video=video,
                video_path=video_path,
            )
        return video_start, saved

    try:
        with _terminate_as_interrupt():
            # The Playwright sync API refuses to run on a thread that owns an asyncio
            # loop (pytest-playwright, async callers), so always give it its own thread.
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(drive_browser)
                try:
                    video_start, saved = future.result()
                except KeyboardInterrupt:
                    stop.set()
                    video_start, saved = future.result()

            if not session_ids:
                raise RecordingError(
                    "The app never started a Shiny session in the browser."
                )
            session_id = session_ids[-1]
            export = _export(app, session_id)
            for entry in export["log"]:
                entry["time"] = max(0.0, float(entry.get("time", 0)) - video_start)
            if redact_inputs:
                redact_export(export)
            for action in actions:
                action["time"] = max(0.0, float(action.get("time", 0)) - video_start)
            return Recording(
                export=export, actions=actions, video_path=saved, session_id=session_id
            )
    finally:
        app.close()
        shutil.rmtree(video_dir, ignore_errors=True)


def serve_and_collect(
    app_file: Path,
    *,
    on_ready: Callable[[str], None],
    wait: Callable[[], None],
    choose: Callable[[list[dict[str, Any]]], list[str]],
) -> list[dict[str, Any]]:
    """Run `app_file` with reactlog on for others to drive; export the chosen sessions."""
    app = _start_app(app_file)
    try:
        with _terminate_as_interrupt():
            on_ready(app.url)
            wait()
            sessions: list[dict[str, Any]] = _get_json(app, "__reactlog__/sessions")
            if not sessions:
                raise RecordingError("No sessions were recorded.")
            return [_export(app, session_id) for session_id in choose(sessions)]
    finally:
        app.close()


_REPLAY_FIXTURES = {"page", "local_app"}


@dataclass
class _ReplayApp:
    """Stands in for the `local_app` fixture; generated tests only read `.url`."""

    url: str


def replay_script(test_file: Path) -> Callable[[Page, str], None]:
    """
    A `record_session` script that runs every `test_*` function in `test_file`.

    Raises
    ------
    RecordingError
        If the file can't be imported, has no tests, or a test needs a fixture other
        than `page` and `local_app`; the returned script raises it when a test
        fails.
    """
    name = f"_reactlog_replay_{test_file.stem}"
    spec = importlib.util.spec_from_file_location(name, test_file)
    if spec is None or spec.loader is None:
        raise RecordingError(f"Cannot import {test_file}.")
    module = importlib.util.module_from_spec(spec)
    # Registered while it runs, so dataclasses and annotations can find the module.
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as err:  # anything the user's file raises at import time
        raise RecordingError(f"Cannot import {test_file}: {err}") from err
    finally:
        sys.modules.pop(name, None)
    tests = [
        fn
        for name, fn in vars(module).items()
        if name.startswith("test_") and callable(fn)
    ]
    if not tests:
        raise RecordingError(f"No test_* functions found in {test_file}.")
    for fn in tests:
        extra = set(inspect.signature(fn).parameters) - _REPLAY_FIXTURES
        if extra:
            raise RecordingError(
                f"{test_file.name}::{fn.__name__} needs fixtures --replay can't "
                "provide: " + ", ".join(sorted(extra))
            )

    def script(page: Page, url: str) -> None:
        fixtures = {"page": page, "local_app": _ReplayApp(url=url)}
        for fn in tests:
            params = inspect.signature(fn).parameters
            try:
                fn(**{k: v for k, v in fixtures.items() if k in params})
            # Assertions, Playwright timeouts, or any other error in the user's test.
            except Exception as err:
                raise RecordingError(
                    f"{test_file.name}::{fn.__name__} failed during replay: "
                    f"{type(err).__name__}: {err}"
                ) from err

    return script
