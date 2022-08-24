from __future__ import annotations

import datetime
import logging
import queue
import random
import socket
import subprocess
import sys
import threading
from enum import Enum
from pathlib import PurePath
from types import TracebackType
from typing import IO, Callable, List, Optional, TextIO, Type, Union

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


class StreamingOutput:
    def __init__(
        self, proc: subprocess.Popen[str], io: IO[str], desc: Optional[str] = None
    ):
        self._proc = proc
        self._io = io
        self._closed = False
        self._lines: List[str] = []
        self._mutex = threading.Lock()
        self._cond = threading.Condition(self._mutex)
        self._thread = threading.Thread(
            group=None, target=self._run, daemon=True, name=desc
        )

        self._thread.start()

    def _run(self):
        try:
            while not self._io.closed:
                try:
                    line = self._io.readline()
                except ValueError:
                    # This is raised when the stream is closed
                    break
                if line is None:
                    break
                if line != "":
                    # logging.warning(f"> {line}")
                    with self._cond:
                        self._lines.append(line)
                        self._cond.notify_all()
        finally:
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


class ShinyAppState(Enum):
    START = 0
    READY = 1
    EXITED = 2


def dummyio() -> TextIO:
    io = TextIO()
    io.close()
    return io


class ShinyAppProc:
    def __init__(self, proc: subprocess.Popen[str], port: int):
        self.proc = proc
        self.port = port
        self.url = f"http://127.0.0.1:{port}/"
        self.stdout = StreamingOutput(proc, proc.stdout or dummyio())
        self.stderr = StreamingOutput(proc, proc.stderr or dummyio())
        self._state = ShinyAppState.START
        threading.Thread(group=None, target=self._run, daemon=True).start()

    def _run(self) -> None:
        self.proc.wait()
        if self.proc.stdout is not None:
            self.proc.stdout.close()
        if self.proc.stderr is not None:
            self.proc.stderr.close()

    def close(self) -> None:
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
        if self.stderr.wait_for(lambda line: "Uvicorn running on1" in line, 10):
            return
        else:
            logging.warning(str(self.stderr))
            raise RuntimeError("Shiny app exited without ever becoming ready")


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

    return pytest.fixture(
        scope=scope,  # type: ignore
    )(fixture_func)


here = PurePath(__file__).parent

# Actual fixtures are here; request them to run the respective Shiny app
airmass_app = create_app_fixture(here / "../examples/airmass/app.py")
cpuinfo_app = create_app_fixture(here / "../examples/cpuinfo/app.py")
