import os
import subprocess
import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.reactive._reactlog._codegen import generate_controller_test
from shiny.reactive._reactlog._record import (
    RecordingError,
    record_session,
    replay_script,
)

APP = Path(__file__).parent / "record_app" / "app.py"


def _record_and_generate(tmp_path: Path) -> Path:
    def script(page: Page, url: str) -> None:
        page.goto(url)
        controller.InputSlider(page, "n").set("7")
        controller.OutputText(page, "out").expect_value("14")

    rec = record_session(APP, video_path=None, script=script)
    test_file = tmp_path / "test_generated.py"
    rel_app = Path(os.path.relpath(APP, tmp_path)).as_posix()
    test_file.write_text(
        generate_controller_test(rec.actions, test_name="record app", app_path=rel_app)
    )
    return test_file


def test_generated_test_passes_against_the_app(tmp_path: Path) -> None:
    test_file = _record_and_generate(tmp_path)
    code = test_file.read_text()
    assert 'controller.InputSlider(page, "n").set("7")' in code
    assert 'controller.OutputText(page, "out").expect_value("14")' in code
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "--browser",
            "chromium",
            "-p",
            "no:cacheprovider",
            "-q",
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_replay_records_the_scripted_session(tmp_path: Path) -> None:
    test_file = _record_and_generate(tmp_path)
    rec = record_session(APP, video_path=None, script=replay_script(test_file))
    assert any(
        x["action"] == "valueChange" and x["label"] == "input.n" and x["value"] == "7"
        for x in rec.export["log"]
    )


def test_replay_rejects_unknown_fixtures(tmp_path: Path) -> None:
    test_file = tmp_path / "test_x.py"
    test_file.write_text("def test_x(page, local_app, tmp_path):\n    pass\n")
    with pytest.raises(RecordingError, match="tmp_path"):
        replay_script(test_file)


def test_replay_reports_failed_assertions(tmp_path: Path, page: Page) -> None:
    test_file = tmp_path / "test_x.py"
    test_file.write_text("def test_x(page):\n    assert False, 'nope'\n")
    with pytest.raises(RecordingError, match="test_x failed during --replay: nope"):
        replay_script(test_file)(page, "http://unused")
