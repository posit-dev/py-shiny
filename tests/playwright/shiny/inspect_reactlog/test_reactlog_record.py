import os
import signal
import sys
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.reactive._reactlog._record import record_session

APP = Path(__file__).parent / "record_app" / "app.py"


def _labels(export: dict[str, Any]) -> set[str]:
    return {x["label"] for x in export["log"] if x["action"] == "define"}


def test_record_session_records_real_events(tmp_path: Path) -> None:
    def script(page: Page, url: str) -> None:
        page.goto(url)
        controller.InputSlider(page, "n").set("7")
        controller.OutputText(page, "out").expect_value("14")

    rec = record_session(APP, video_path=tmp_path / "v.webm", script=script)
    assert {"input.n", "reactive.calc doubled", "output out"} <= _labels(rec.export)
    assert any(a.get("type") == "input" and a.get("name") == "n" for a in rec.actions)
    assert rec.video_path is not None and rec.video_path.stat().st_size > 0
    assert all(0 <= x["time"] < 600 for x in rec.export["log"])  # rebased seconds


def test_record_session_survives_window_close(tmp_path: Path) -> None:
    def script(page: Page, url: str) -> None:
        page.goto(url)
        controller.InputSlider(page, "n").set("5")
        controller.OutputText(page, "out").expect_value("10")
        page.close()

    rec = record_session(APP, video_path=None, script=script)
    assert any(a.get("name") == "n" for a in rec.actions)
    assert "output out" in _labels(rec.export)


def test_record_session_exports_latest_session_after_reload(tmp_path: Path) -> None:
    seen: list[str] = []

    def script(page: Page, url: str) -> None:
        page.goto(url)
        controller.OutputText(page, "out").expect_value("6")
        seen.append(page.evaluate("Shiny.shinyapp.config.sessionId"))
        page.reload()
        controller.InputSlider(page, "n").set("4")
        controller.OutputText(page, "out").expect_value("8")
        seen.append(page.evaluate("Shiny.shinyapp.config.sessionId"))

    rec = record_session(APP, video_path=None, script=script)
    assert rec.session_id == seen[-1] != seen[0]


def test_record_session_keeps_export_when_browser_quits(tmp_path: Path) -> None:
    def script(page: Page, url: str) -> None:
        page.goto(url)
        controller.OutputText(page, "out").expect_value("6")
        browser = page.context.browser
        assert browser is not None
        browser.close()

    rec = record_session(APP, video_path=tmp_path / "v.webm", script=script)
    assert rec.video_path is None
    assert "output out" in _labels(rec.export)


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX signals")
def test_record_session_keeps_export_when_driver_dies(
    tmp_path: Path,
) -> None:
    # A terminal's Ctrl+C reaches the Playwright driver too; once it is gone every
    # Playwright call fails with a plain Exception ("Connection closed").
    def script(page: Page, url: str) -> None:
        page.goto(url)
        controller.OutputText(page, "out").expect_value("6")
        driver = page._impl_obj._connection._transport._proc  # type: ignore
        os.kill(driver.pid, signal.SIGKILL)  # pyright: ignore

    rec = record_session(APP, video_path=tmp_path / "v.webm", script=script)
    assert "output out" in _labels(rec.export)


def _type_pw_and_txt(page: Page, url: str) -> None:
    page.goto(url)
    controller.OutputText(page, "out").expect_value("6")
    controller.InputPassword(page, "pw").set("hunter2")
    controller.InputText(page, "txt").set("hello")
    # Wait for the server to see the text input before the recording ends.
    page.wait_for_function("Shiny.shinyapp.$inputValues.txt === 'hello'")


def _last_value(actions: list[dict[str, Any]], name: str) -> Any:
    return [a["value"] for a in actions if a.get("name") == name][-1]


def _input_values(export: dict[str, Any], label: str) -> list[str]:
    return [
        x["value"]
        for x in export["log"]
        if x["action"] == "valueChange" and x.get("label") == label
    ]


@pytest.mark.parametrize("redact_inputs", [False, True])
def test_record_session_redacts_inputs(redact_inputs: bool) -> None:
    rec = record_session(
        APP,
        video_path=None,
        script=_type_pw_and_txt,
        redact_inputs=redact_inputs,
    )
    assert _last_value(rec.actions, "pw") == "[REDACTED]"
    txt_values = _input_values(rec.export, "input.txt")
    assert txt_values
    if redact_inputs:
        assert _last_value(rec.actions, "txt") == "[REDACTED]"
        assert set(txt_values) == {"[REDACTED]"}
        assert set(_input_values(rec.export, "input.pw")) == {"[REDACTED]"}
    else:
        assert _last_value(rec.actions, "txt") == "hello"
        assert "'hello'" in txt_values
