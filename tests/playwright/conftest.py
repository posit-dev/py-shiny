from __future__ import annotations

import datetime
import functools
import logging
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import PurePath
from time import sleep
from types import TracebackType
from typing import (
    IO,
    Any,
    Callable,
    Generator,
    List,
    Literal,
    Optional,
    TextIO,
    Type,
    Union,
)

import pytest

import shiny._utils

__all__ = (
    "ShinyAppProc",
    "create_app_fixture",
    "create_doc_example_core_fixture",
    "create_example_fixture",
    "local_app",
    "run_shiny_app",
    "expect_to_change",
    "retry_with_timeout",
)

here = PurePath(__file__).parent
here_root = here.parent.parent


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
        sleep(0.5)
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
            return "Uvicorn running on" in line

        if self.stderr.wait_for(stderr_uvicorn, timeoutSecs=timeoutSecs):
            return
        else:
            raise RuntimeError(
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
    if port == 0:
        port = shiny._utils.random_port()

    child = subprocess.Popen(
        [sys.executable, "-m", "shiny", "run", "--port", str(port), str(app_file)],
        bufsize=bufsize,
        executable=sys.executable,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        encoding="utf-8",
    )

    # TODO: Detect early exit

    sa = ShinyAppProc(child, port)
    if wait_for_start:
        sa.wait_until_ready(timeout_secs)
    return sa


def local_app_fixture_gen(app: PurePath | str):
    sa = run_shiny_app(app, wait_for_start=False)
    try:
        with sa:
            sa.wait_until_ready(30)
            yield sa
    finally:
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


def create_example_fixture(
    example_name: str,
    example_file: str = "app.py",
    scope: ScopeName = "module",
):
    """Used to create app fixtures from apps in py-shiny/examples"""
    return create_app_fixture(
        here_root / "examples" / example_name / example_file, scope
    )


def create_doc_example_fixture(
    example_name: str,
    example_file: str = "app.py",
    scope: ScopeName = "module",
):
    """Used to create app fixtures from apps in py-shiny/shiny/api-examples"""
    return create_app_fixture(
        here_root / "shiny/api-examples" / example_name / example_file, scope
    )


def create_doc_example_core_fixture(
    example_name: str,
    scope: ScopeName = "module",
):
    """Used to create app fixtures from ``app-core.py`` example apps in py-shiny/shiny/api-examples"""
    return create_doc_example_fixture(example_name, "app-core.py", scope)


def create_doc_example_express_fixture(
    example_name: str,
    scope: ScopeName = "module",
):
    """Used to create app fixtures from ``app-express.py`` example apps in py-shiny/shiny/api-examples"""
    return create_doc_example_fixture(example_name, "app-express.py", scope)


def x_create_doc_example_fixture(example_name: str, scope: ScopeName = "module"):
    """Used to create app fixtures from apps in py-shiny/shiny/examples"""
    return create_app_fixture(
        here_root / "shiny/experimental/api-examples" / example_name / "app.py", scope
    )


@pytest.fixture(scope="module")
def local_app(request: pytest.FixtureRequest) -> Generator[ShinyAppProc, None, None]:
    app_gen = local_app_fixture_gen(PurePath(request.path).parent / "app.py")
    yield next(app_gen)


@contextmanager
def expect_to_change(
    func: Callable[[], Any], timeoutSecs: float = 10
) -> Generator[None, None, None]:
    """
    Context manager that yields when the value returned by func() changes. Use this
    around code that has a side-effect of changing some state asynchronously (such as
    all browser actions), to prevent moving onto the next step of the test until this
    one has actually taken effect.

    Raises TimeoutError if the value does not change within timeoutSecs.

    Parameters
    ----------
    func
        A function that returns a value. The value returned by this function is
        compared to the value returned by subsequent calls to this function.
    timeoutSecs
        How long to wait for the value to change before raising TimeoutError.

    Example
    -------

        with expect_to_change(lambda: page.locator("#name").value()):
            page.keyboard.send_keys("hello")

    """

    original_value = func()
    yield

    @retry_with_timeout(timeoutSecs)
    def wait_for_change():
        if func() == original_value:
            raise AssertionError("Value did not change")

    wait_for_change()


def retry_with_timeout(timeout: float = 30):
    """
    Decorator that retries a function until 1) it succeeds, 2) fails with a
    non-assertion error, or 3) repeatedly fails with an AssertionError for longer than
    the timeout. If the timeout elapses, the last AssertionError is raised.

    Parameters
    ----------
    timeout
        How long to wait for the function to succeed before raising the last
        AssertionError.

    Returns
    -------
    A decorator that can be applied to a function.

    Example
    -------

        @retry_with_timeout(30)
        def try_to_find_element():
            if not page.locator("#name").exists():
                raise AssertionError("Element not found")

        try_to_find_element()
    """

    def decorator(func: Callable[[], None]) -> Callable[[], None]:
        @functools.wraps(func)
        def wrapper() -> None:
            start = time.time()
            while True:
                try:
                    return func()
                except AssertionError as e:
                    if time.time() - start > timeout:
                        raise e
                    time.sleep(0.1)

        return wrapper

    return decorator
