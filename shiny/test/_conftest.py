from __future__ import annotations

import datetime
import logging
import subprocess
import sys
import threading
from pathlib import PurePath
from types import TracebackType
from typing import IO, Callable, Generator, List, Literal, Optional, TextIO, Type, Union

import pytest

import shiny._utils

__all__ = (
    "ShinyAppProc",
    "create_app_fixture",
    "local_app",
    "run_shiny_app",
)

from playwright.sync_api import BrowserContext, Page


# Make a single page fixture that can be used by all tests
@pytest.fixture(scope="session")
# By using a single page, the browser is only launched once and all tests run in the same tab / page.
def session_page(browser: BrowserContext) -> Page:
    return browser.new_page()


@pytest.fixture(scope="function")
# By going to `about:blank`, we _reset_ the page to a known state before each test.
# It is not perfect, but it is faster than making a new page for each test.
# This must be done before each test
def page(session_page: Page) -> Page:
    session_page.goto("about:blank")
    # Reset screen size to 1080p
    session_page.set_viewport_size({"width": 1920, "height": 1080})
    return session_page


class OutputStream:
    """Designed to wrap an IO[str] and accumulate the output using a bg thread

    Also allows for blocking waits for particular lines."""

    def __init__(self, io: IO[str], desc: Optional[str] = None):
        self._io = io
        self._closed = False
        self._lines: List[str] = []
        self._cond = threading.Condition()
        self._thread = threading.Thread(
            group=None, target=self._run, daemon=True, name=desc
        )

        self._thread.start()

    def _run(self):
        """Pump lines into self._lines in a tight loop."""

        try:
            while not self._io.closed:
                try:
                    line = self._io.readline()
                except ValueError:
                    # This is raised when the stream is closed
                    break
                if line != "":
                    with self._cond:
                        self._lines.append(line)
                        self._cond.notify_all()
        finally:
            # If we got here, we're finished reading self._io and need to signal any
            # waiters that we're done and they'll never hear from us again.
            with self._cond:
                self._closed = True
                self._cond.notify_all()

    def wait_for(self, predicate: Callable[[str], bool], timeoutSecs: float) -> bool:
        timeoutAt = datetime.datetime.now() + datetime.timedelta(seconds=timeoutSecs)
        pos = 0
        with self._cond:
            while True:
                while pos < len(self._lines):
                    if predicate(self._lines[pos]):
                        return True
                    pos += 1
                if self._closed:
                    return False
                else:
                    remaining = (timeoutAt - datetime.datetime.now()).total_seconds()
                    if remaining < 0 or not self._cond.wait(timeout=remaining):
                        # Timed out
                        raise TimeoutError(
                            "Timeout while waiting for Shiny app to become ready"
                        )

    def __str__(self):
        with self._cond:
            return "".join(self._lines)


def dummyio() -> TextIO:
    io = TextIO()
    io.close()
    return io


class ShinyAppProc:
    def __init__(self, proc: subprocess.Popen[str], port: int):
        self.proc = proc
        self.port = port
        self.url = f"http://127.0.0.1:{port}/"
        self.stdout = OutputStream(proc.stdout or dummyio())
        self.stderr = OutputStream(proc.stderr or dummyio())
        threading.Thread(group=None, target=self._run, daemon=True).start()

    def _run(self) -> None:
        self.proc.wait()
        if self.proc.stdout is not None:
            self.proc.stdout.close()
        if self.proc.stderr is not None:
            self.proc.stderr.close()

    def close(self) -> None:
        # from time import sleep
        # sleep(0.5)
        self.proc.terminate()

    def __enter__(self) -> ShinyAppProc:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ):
        self.close()

    def wait_until_ready(self, timeoutSecs: float) -> None:
        error_lines: List[str] = []

        def stderr_uvicorn(line: str) -> bool:
            error_lines.append(line)
            if "error while attempting to bind on address" in line:
                raise ConnectionError(f"Error while staring shiny app: `{line}`")
            return "Uvicorn running on" in line

        if self.stderr.wait_for(stderr_uvicorn, timeoutSecs=timeoutSecs):
            return
        else:
            raise TimeoutError(
                "Shiny app exited without ever becoming ready. Waiting for 'Uvicorn running on' in stderr. Last 20 lines of stderr:\n"
                + "\n".join(error_lines[-20:])
            )


def run_shiny_app(
    app_file: Union[str, PurePath],
    *,
    port: int = 0,
    cwd: Optional[str] = None,
    wait_for_start: bool = True,
    timeout_secs: float = 10,
    bufsize: int = 64 * 1024,
) -> ShinyAppProc:
    shiny_port = port if port != 0 else shiny._utils.random_port()

    child = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "shiny",
            "run",
            "--port",
            str(shiny_port),
            str(app_file),
        ],
        bufsize=bufsize,
        executable=sys.executable,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        encoding="utf-8",
    )

    # TODO: Detect early exit

    sa = ShinyAppProc(child, shiny_port)
    if wait_for_start:
        sa.wait_until_ready(timeout_secs)
    return sa


# Attempt up to 3 times to start the app, with a random port each time
def local_app_fixture_gen(app: PurePath | str):

    has_yielded_app = False
    remaining_attempts = 3
    while not has_yielded_app and remaining_attempts > 0:
        remaining_attempts -= 1

        # Make shiny process
        sa = run_shiny_app(app, wait_for_start=False, port=0)
        try:
            # enter / exit shiny context manager; (closes streams on exit)
            with sa:
                # Wait for shiny app to start
                # Could throw a `ConnectionError` if the port is already in use
                sa.wait_until_ready(30)
                # Run app!
                has_yielded_app = True
                yield sa
        except ConnectionError as e:
            if remaining_attempts == 0:
                # Ran out of attempts!
                raise e
            print(f"Failed to bind to port: {e}", file=sys.stderr)
            # Try again with a new port!
        finally:
            if has_yielded_app:
                logging.warning("Application output:\n" + str(sa.stderr))


ScopeName = Literal["session", "package", "module", "class", "function"]


def create_app_fixture(
    app: Union[PurePath, str],
    scope: ScopeName = "module",
):
    @pytest.fixture(scope=scope)
    def fixture_func():
        # Pass through `yield` via `next(...)` call
        # (`yield` must be on same line as `next`!)
        app_gen = local_app_fixture_gen(app)
        yield next(app_gen)

    return fixture_func


@pytest.fixture(scope="module")
def local_app(request: pytest.FixtureRequest) -> Generator[ShinyAppProc, None, None]:
    app_gen = local_app_fixture_gen(PurePath(request.path).parent / "app.py")
    yield next(app_gen)
