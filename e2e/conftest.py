from __future__ import annotations

import datetime
import queue
import random
import socket
import subprocess
import sys
import threading
from enum import Enum
from pathlib import PurePath
from types import TracebackType
from typing import Optional, TextIO, Type, Union

import pytest


def random_port():
    while True:
        port = random.randint(1024, 49151)
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except Exception:
                # Let's just assume that port was in use; try again
                continue


def pipe_reader(stream: TextIO, queue: queue.Queue[str]):
    while not stream.closed:
        try:
            line = stream.readline()
        except ValueError:
            # This is raised when the stream is closed
            break
        if line is None:
            break
        if line != "":
            # print(f"> {line}", end="")
            queue.put(line)


class ShinyAppState(Enum):
    START = 0
    READY = 1
    EXITED = 2


class ShinyAppProc:
    def __init__(self, proc: subprocess.Popen[str], port: int):
        self.proc = proc
        self.port = port
        self.url = f"http://127.0.0.1:{port}/"
        self.stdout: queue.Queue[str] = queue.Queue()
        self.stderr: queue.Queue[str] = queue.Queue()
        self._state = ShinyAppState.START

        self.stdout_thread: threading.Thread = threading.Thread(
            group=None,
            target=pipe_reader,
            args=(proc.stdout, self.stdout),
            name="shiny_stdout_reader",
            daemon=True,
        )
        self.stdout_thread.start()
        self.stderr_thread: threading.Thread = threading.Thread(
            group=None,
            target=pipe_reader,
            args=(proc.stderr, self.stderr),
            name="shiny_stderr_reader",
            daemon=True,
        )
        self.stderr_thread.start()

    def close(self) -> None:
        self.proc.terminate()
        if self.proc.stdout is not None:
            self.proc.stdout.close()
        if self.proc.stderr is not None:
            self.proc.stderr.close()

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
        timeoutAt = datetime.datetime.now() + datetime.timedelta(seconds=timeoutSecs)
        while True:
            self.proc.poll()

            if self._state is ShinyAppState.EXITED or self.proc.returncode is not None:
                raise RuntimeError("Shiny app process has exited")
            elif self._state is ShinyAppState.READY:
                return
            elif self._state is ShinyAppState.START:
                remaining = timeoutAt - datetime.datetime.now()
                if remaining.total_seconds() < 0:
                    raise TimeoutError(
                        "Timeout expired while waiting for Shiny app to be ready"
                    )
                try:
                    line = self.stderr.get(
                        block=True, timeout=min(0.2, remaining.total_seconds())
                    )
                except queue.Empty:
                    continue
                if "Uvicorn running on" in line:
                    self._state = ShinyAppState.READY
                    return
            else:
                raise RuntimeError(f"Unknown ShinyAppProc._state value: {self._state}")


def run_shiny_app(
    app_file: Union[str, PurePath],
    *,
    port: Optional[int] = None,
    cwd: Optional[str] = None,
    wait_for_start: bool = True,
    timeout_secs: float = 10,
    bufsize: int = 64 * 1024,
) -> ShinyAppProc:
    if port is None:
        port = random_port()

    child = subprocess.Popen(
        [sys.executable, "-m", "shiny", "run", "--port", str(port), str(app_file)],
        bufsize=bufsize,
        executable=sys.executable,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        encoding="utf-8",
    )

    # TODO: If wait_for_start, ensure the app is listening before returning
    # TODO: Detect early exit

    sa = ShinyAppProc(child, port)
    if wait_for_start:
        sa.wait_until_ready(timeout_secs)
    return sa


def create_app_fixture(app: Union[PurePath, str], scope: str = "module"):
    def fixture_func():
        with run_shiny_app(app) as sa:
            yield sa

    return pytest.fixture(scope=scope)(fixture_func)


here = PurePath(__file__).parent

# Actual fixtures are here; request them to run the respective Shiny app
airmass_app = create_app_fixture(here / "../examples/airmass/app.py")
cpuinfo_app = create_app_fixture(here / "../examples/cpuinfo/app.py")
