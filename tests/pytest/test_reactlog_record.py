import io
import threading
from pathlib import Path

import pytest

from shiny.reactive._reactlog._record import (
    RecordingError,
    _start_stdin_reader,
    record_session,
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
