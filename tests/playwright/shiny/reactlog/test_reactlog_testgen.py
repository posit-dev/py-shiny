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


def _run_pytest(test_file: Path, *args: str) -> None:
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
            *args,
        ],
        capture_output=True,
        text=True,
        cwd=test_file.parent,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_generated_test_passes_against_the_app(tmp_path: Path) -> None:
    test_file = _record_and_generate(tmp_path)
    code = test_file.read_text()
    assert 'controller.InputSlider(page, "n").set("7")' in code
    assert 'controller.OutputText(page, "out").expect_value("14")' in code
    _run_pytest(test_file)


def test_generated_test_asserts_settled_values(tmp_path: Path) -> None:
    def script(page: Page, url: str) -> None:
        page.goto(url)
        # Each `set` fires several input events; the next input follows at once.
        controller.InputCheckboxGroup(page, "cg").set(["x", "z"])
        controller.InputText(page, "txt").set("hi")
        controller.InputDate(page, "d").set("02/03/2024")
        controller.InputDateRange(page, "dr").set(("03/01/2024", "03/02/2024"))
        controller.InputSlider(page, "n").set("7")
        controller.OutputCode(page, "code_out").expect_value("n=7")
        controller.OutputText(page, "dates_out").expect_value(
            "d=2024-02-03 dr=(datetime.date(2024, 3, 1), datetime.date(2024, 3, 2))"
        )

    rec = record_session(APP, video_path=None, script=script)
    code = generate_controller_test(
        rec.actions,
        test_name="record app",
        app_path=Path(os.path.relpath(APP, tmp_path)).as_posix(),
    )
    assert 'controller.InputCheckboxGroup(page, "cg").set(["x", "z"])' in code
    assert 'controller.InputDate(page, "d").set("02/03/2024")' in code
    assert 'controller.OutputCode(page, "code_out").expect_value("n=7")' in code
    assert """expect_value("cg=('x', 'z')")""" in code
    assert """expect_value("cg=('x',)")""" not in code
    # Pausing after every action must not change what the test sees.
    slow = "".join(
        line
        + (
            "    page.wait_for_timeout(700)\n"
            if ".set(" in line or ".click(" in line
            else ""
        )
        for line in code.splitlines(keepends=True)
    )
    test_file = tmp_path / "test_generated.py"
    test_file.write_text(slow)
    _run_pytest(test_file, "-W", "error")


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
    with pytest.raises(
        RecordingError, match="test_x failed during replay: AssertionError: nope"
    ):
        replay_script(test_file)(page, "http://unused")


def test_replay_reports_playwright_errors_cleanly(tmp_path: Path) -> None:
    test_file = tmp_path / "test_x.py"
    test_file.write_text(
        "def test_click(page, local_app):\n"
        "    page.goto(local_app.url)\n"
        "    page.locator('#nope').click(timeout=500)\n"
    )
    with pytest.raises(
        RecordingError, match="test_x.py::test_click failed during replay"
    ):
        record_session(APP, video_path=None, script=replay_script(test_file))


def test_replay_supports_dataclasses_and_reports_import_errors(tmp_path: Path) -> None:
    ok = tmp_path / "test_dc.py"
    ok.write_text(
        "from __future__ import annotations\n"
        "from dataclasses import dataclass\n\n"
        "@dataclass\nclass Point:\n    x: int\n\n"
        "def test_dc(page):\n    pass\n"
    )
    replay_script(ok)
    bad = tmp_path / "test_bad.py"
    bad.write_text("raise ValueError('boom')\n")
    with pytest.raises(RecordingError, match="Cannot import .*boom"):
        replay_script(bad)


def test_replay_notes_when_several_sessions_were_recorded(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    test_file = tmp_path / "test_two.py"
    test_file.write_text(
        "from shiny.playwright import controller\n\n"
        "def test_one(page, local_app):\n"
        "    page.goto(local_app.url)\n"
        "    controller.OutputText(page, 'out').expect_value('6')\n\n"
        "def test_two(page, local_app):\n"
        "    page.goto(local_app.url)\n"
        "    controller.InputSlider(page, 'n').set('4')\n"
        "    controller.OutputText(page, 'out').expect_value('8')\n"
    )
    record_session(APP, video_path=None, script=replay_script(test_file))
    assert "2 sessions were recorded; exported the last" in capsys.readouterr().err
