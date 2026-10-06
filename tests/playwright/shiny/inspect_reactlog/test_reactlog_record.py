from pathlib import Path
from typing import Any

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
