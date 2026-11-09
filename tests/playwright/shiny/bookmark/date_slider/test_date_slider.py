import json
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from shiny.playwright.controller import (
    InputActionButton,
    InputBookmarkButton,
    InputSlider,
    InputSliderRange,
    OutputCode,
)
from shiny.run import run_shiny_app


@pytest.mark.parametrize("store", ["url", "server"])
def test_date_slider_bookmark(
    page: Page, store: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SHINY_SLIDER_BOOKMARK_STORE", store)
    monkeypatch.setenv("SHINY_SLIDER_BOOKMARK_DIR", str(tmp_path))
    with run_shiny_app(Path(__file__).with_name("app.py"), wait_for_start=True) as app:
        page.goto(app.url)
        values = OutputCode(page, "values")
        expect(values.loc).to_contain_text('"day": "2026-02-01"')
        InputActionButton(page, "change").click()
        saved = json.dumps(
            dict(
                day="2026-06-15",
                days=["2026-06-15", "2026-09-20"],
                moment="2026-06-15 12:34:56",
                moments=["2026-06-15 12:34:56", "2026-09-20 01:02:03"],
                number=7,
                numbers=[6, 9],
                module_day="2026-06-16",
            )
        )
        # Wait for all client updates to reach the server before saving.
        values.expect_value(saved)
        InputBookmarkButton(page).click()
        link = page.locator("div.modal-body > textarea")
        expect(link).to_have_value(
            re.compile("_inputs_" if store == "url" else "_state_id_")
        )
        bookmark_url = link.input_value()

        # A fresh navigation avoids Firefox's form restoration on reload.
        page.goto(bookmark_url)
        values.expect_value(saved)
        InputSlider(page, "day").expect_value("2026-06-15")
        InputSliderRange(page, "days").expect_value(("2026-06-15", "2026-09-20"))
        InputSlider(page, "moment").expect_value("2026-06-15 12:34:56")
        InputSliderRange(page, "moments").expect_value(
            ("2026-06-15 12:34:56", "2026-09-20 01:02:03")
        )
        InputSlider(page, "number").expect_value("7")
        InputSliderRange(page, "numbers").expect_value(("6", "9"))
        InputSlider(page, "m-day").expect_value("2026-06-16")
