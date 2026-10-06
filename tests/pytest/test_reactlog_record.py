import io
import threading
from pathlib import Path

import pytest

from shiny.reactive._reactlog._record import (
    RecordingError,
    _start_stdin_reader,
    _wait_for_enter_or_close,
    record_session,
    redact_export,
)


def test_record_session_reports_app_start_failure(tmp_path: Path) -> None:
    bad = tmp_path / "app.py"
    bad.write_text("def broken(:\n")
    with pytest.raises(RecordingError, match="Failed to start"):
        record_session(bad, video_path=None, script=lambda page, url: None)


def test_stdin_reader_not_started_without_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    done = threading.Event()
    before = threading.active_count()
    assert _start_stdin_reader(done) is False
    assert threading.active_count() == before
    assert not done.is_set()


def test_stdin_reader_ignores_eof_on_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeTty(io.StringIO):
        def isatty(self) -> bool:
            return True

    monkeypatch.setattr("sys.stdin", FakeTty(""))
    done = threading.Event()
    assert _start_stdin_reader(done) is True
    assert not done.wait(timeout=0.2)

    monkeypatch.setattr("sys.stdin", FakeTty("\n"))
    done = threading.Event()
    assert _start_stdin_reader(done) is True
    assert done.wait(timeout=2)


def test_wait_loop_returns_when_stop_is_set() -> None:
    class FakePage:
        def is_closed(self) -> bool:
            return False

        def wait_for_timeout(self, ms: float) -> None:
            stop.set()

    stop = threading.Event()
    _wait_for_enter_or_close(FakePage(), 60.0, stop)  # type: ignore[arg-type]
    assert stop.is_set()


def test_redact_export_only_touches_input_value_changes() -> None:
    export = {
        "log": [
            {"action": "valueChange", "type": "input", "value": "x"},
            {"action": "valueChange", "type": "calc", "value": "y"},
        ]
    }
    redact_export(export)
    assert [e["value"] for e in export["log"]] == ["[REDACTED]", "y"]
