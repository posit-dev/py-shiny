from pathlib import Path

import pytest

from shiny.reactive._reactlog._record import RecordingError, record_session


def test_record_session_reports_app_start_failure(tmp_path: Path) -> None:
    bad = tmp_path / "app.py"
    bad.write_text("def broken(:\n")
    with pytest.raises(RecordingError, match="Failed to start"):
        record_session(bad, video_path=None, script=lambda page, url: None)
