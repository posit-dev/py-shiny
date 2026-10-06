import io
import threading
from pathlib import Path
from typing import Any

import pytest

from shiny.reactive._reactlog import _record
from shiny.reactive._reactlog._record import (
    RecordingError,
    _close_browser,
    _start_stdin_reader,
    _wait_for_enter_or_close,
    record_session,
    redact_export,
    serve_and_collect,
)


def test_record_session_reports_app_start_failure(tmp_path: Path) -> None:
    bad = tmp_path / "app.py"
    bad.write_text("def broken(:\n")
    with pytest.raises(RecordingError, match="Failed to start") as err:
        record_session(bad, video_path=None, script=lambda page, url: None)
    lines = str(err.value).splitlines()
    assert lines[0] == f"Failed to start Shiny app {bad}:"
    assert 1 < len(lines) <= 6 and all(line.strip() for line in lines)
    assert "SyntaxError" in lines[-1]


def test_start_app_runs_app_in_its_own_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A terminal's Ctrl+C goes to the whole process group; the app must outlive it
    # so the recording can still be exported.
    calls: list[dict[str, Any]] = []

    def fake_run(app_file: Path, **kwargs: Any) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(_record, "run_shiny_app", fake_run)
    _record._start_app(Path("app.py"))  # pyright: ignore[reportPrivateUsage]
    assert calls[0]["start_new_session"] is True


def test_serve_and_collect_reports_app_that_stopped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = tmp_path / "app.py"
    app.write_text("from shiny.express import ui\nui.p('hi')\n")
    procs: list[Any] = []
    start_app = _record._start_app  # pyright: ignore[reportPrivateUsage]

    def start_and_keep(app_file: Path) -> Any:
        procs.append(start_app(app_file))
        return procs[-1]

    def kill_app() -> None:
        procs[0].proc.kill()
        procs[0].proc.wait()

    monkeypatch.setattr(_record, "_start_app", start_and_keep)
    with pytest.raises(RecordingError, match="The app stopped before"):
        serve_and_collect(
            app,
            on_ready=lambda url: None,
            wait=kill_app,
            choose=lambda sessions: [s["id"] for s in sessions],
        )


class _Closable:
    def __init__(self, fail: Exception | None = None) -> None:
        self.fail = fail
        self.closed = False

    def is_closed(self) -> bool:
        return self.closed

    def close(self) -> None:
        if self.fail is not None:
            raise self.fail
        self.closed = True


class _Video:
    def __init__(self, fail: Exception | None = None) -> None:
        self.fail = fail

    def save_as(self, path: str) -> None:
        if self.fail is not None:
            raise self.fail
        Path(path).write_text("video")


def _close(
    tmp_path: Path,
    *,
    context: _Closable | None = None,
    video: _Video | None = None,
    browser: _Closable | None = None,
) -> Path | None:
    return _close_browser(
        _Closable(),  # type: ignore[arg-type]
        context=context or _Closable(),  # type: ignore[arg-type]
        browser=browser or _Closable(),  # type: ignore[arg-type]
        video=video or _Video(),  # type: ignore[arg-type]
        video_path=tmp_path / "v.webm",
    )


def test_close_browser_saves_video(tmp_path: Path) -> None:
    assert _close(tmp_path) == tmp_path / "v.webm"


def test_close_browser_keeps_saved_video_when_browser_close_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dead = _Closable(Exception("Connection closed while reading from the driver"))
    assert _close(tmp_path, browser=dead) == tmp_path / "v.webm"
    assert "Video could not be saved" not in capsys.readouterr().err


@pytest.mark.parametrize(
    "where", ["context", "video"], ids=["driver-died", "disk-error"]
)
def test_close_browser_warns_when_video_is_lost(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], where: str
) -> None:
    if where == "context":
        saved = _close(tmp_path, context=_Closable(Exception("Connection closed")))
    else:
        saved = _close(tmp_path, video=_Video(OSError("disk full")))
    assert saved is None
    assert "Video could not be saved" in capsys.readouterr().err


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
