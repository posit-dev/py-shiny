"""Tests for shiny.run._run helpers."""

from __future__ import annotations

import io
from typing import Callable

import pytest

from shiny.run._run import OutputStream, ShinyAppProc, run_shiny_app


class DummyIO:
    def __init__(self, lines: list[str]):
        self._lines = lines
        self.closed = False

    def readline(self) -> str:
        if self._lines:
            return self._lines.pop(0)
        self.closed = True
        return ""

    def close(self) -> None:
        self.closed = True


class DummyProc:
    def __init__(self):
        self.stdout = None
        self.stderr = None
        self.terminated = False

    def wait(self) -> int:
        return 0

    def terminate(self) -> None:
        self.terminated = True


def test_output_stream_wait_for_and_str() -> None:
    stream = DummyIO(["one\n", "ready\n"])
    out = OutputStream(stream)
    assert out.wait_for(lambda line: "ready" in line, timeout_secs=1) is True
    assert "one" in str(out)


def test_output_stream_wait_for_false_when_closed() -> None:
    stream = DummyIO(["one\n"])
    out = OutputStream(stream)
    assert out.wait_for(lambda line: "missing" in line, timeout_secs=1) is False


def test_run_shiny_app_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    proc = DummyProc()

    def fake_popen(*args, **kwargs):
        return proc

    calls: list[str] = []

    def fake_wait(self, timeout_secs: float) -> None:
        calls.append("wait")
        if len(calls) == 1:
            raise ConnectionError("bind error")

    monkeypatch.setattr("subprocess.Popen", fake_popen)
    monkeypatch.setattr(ShinyAppProc, "wait_until_ready", fake_wait)

    sa = run_shiny_app("app.py", start_attempts=2, port=1234, wait_for_start=True)
    assert isinstance(sa, ShinyAppProc)
    assert len(calls) == 2


def test_run_shiny_app_no_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    proc = DummyProc()

    def fake_popen(*args, **kwargs):
        return proc

    monkeypatch.setattr("subprocess.Popen", fake_popen)

    sa = run_shiny_app("app.py", port=1234, wait_for_start=False)
    assert isinstance(sa, ShinyAppProc)
