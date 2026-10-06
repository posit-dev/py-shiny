"""Record a real Shiny session in a browser (or wait for one) and fetch its reactlog."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from ...run._run import ShinyAppProc, run_shiny_app

if TYPE_CHECKING:
    from playwright.sync_api import Page

_APP_ENV = {"SHINY_REACTLOG": "1", "SHINY_TESTMODE": "1", "PYTHONUNBUFFERED": "1"}

# Streams browser actions and session ids to Python as they happen, so closing the
# window or reloading the page loses nothing.
RECORDER_SCRIPT = r"""
(() => {
  const redactAll = !!window.__shinyReactlogRedactAll;
  const send = (item) => {
    item.time = Date.now() / 1000;
    if (window.__shinyReactlogAction) window.__shinyReactlogAction(item);
  };
  const sensitive = (name, el) => {
    if (redactAll) return true;
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
      send({
        type: "input",
        name: e.name,
        value: sensitive(e.name, el) ? "[REDACTED]" : e.value,
        inputType: e.inputType || "",
      });
    });
    $(document).on("shiny:value.shinyReactlog", (e) => {
      send({ type: "output", name: e.name });
    });
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
        return run_shiny_app(app_file, wait_for_start=True, env=_APP_ENV)
    except Exception as err:  # run_shiny_app raises various errors for a bad app
        raise RecordingError(f"Failed to start Shiny app {app_file}: {err}") from err


def _get_json(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _export(app_url: str, session_id: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"session_id": session_id})
    return _get_json(f"{app_url}__reactlog__/export?{query}")


def _wait_for_enter_or_close(page: Page, timeout_secs: float) -> None:
    from playwright.sync_api import Error as PlaywrightError

    done = threading.Event()

    def read_stdin() -> None:
        sys.stdin.readline()
        done.set()

    threading.Thread(target=read_stdin, daemon=True).start()
    sys.stderr.write(
        "Recording. Interact with the app, then press Enter here "
        "(or close the browser window) to finish.\n"
    )
    deadline = time.time() + timeout_secs
    while not done.is_set() and time.time() < deadline and not page.is_closed():
        try:
            # Also lets Playwright deliver exposed-function calls.
            page.wait_for_timeout(250)
        except PlaywrightError:
            break


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
            if redact_inputs:
                context.add_init_script("window.__shinyReactlogRedactAll = true;")
            context.add_init_script(RECORDER_SCRIPT)
            page = context.new_page()
            video_start = time.time()
            video = page.video
            if script is not None:
                script(page, app.url)
            else:
                page.goto(app.url)
                _wait_for_enter_or_close(page, timeout_secs)
            if not page.is_closed():
                page.close()
            context.close()
            saved: Path | None = None
            if video is not None and video_path is not None:
                video_path.parent.mkdir(parents=True, exist_ok=True)
                video.save_as(str(video_path))
                saved = video_path
            browser.close()
        return video_start, saved

    try:
        # The Playwright sync API refuses to run on a thread that owns an asyncio
        # loop (pytest-playwright, async callers), so always give it its own thread.
        with ThreadPoolExecutor(max_workers=1) as executor:
            video_start, saved = executor.submit(drive_browser).result()

        if not session_ids:
            raise RecordingError(
                "The app never started a Shiny session in the browser."
            )
        session_id = session_ids[-1]
        export = _export(app.url, session_id)
        for entry in export["log"]:
            entry["time"] = max(0.0, float(entry.get("time", 0)) - video_start)
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
        on_ready(app.url)
        wait()
        sessions: list[dict[str, Any]] = _get_json(f"{app.url}__reactlog__/sessions")
        if not sessions:
            raise RecordingError("No sessions were recorded.")
        return [_export(app.url, session_id) for session_id in choose(sessions)]
    finally:
        app.close()
