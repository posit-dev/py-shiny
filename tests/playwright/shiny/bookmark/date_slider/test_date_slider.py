import json
import re
from pathlib import Path
from urllib.parse import urlencode

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
    page: Page, store: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SHINY_SLIDER_BOOKMARK_STORE", store)
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


def test_slider_bookmark_wrong_length_range(page: Page) -> None:
    # A hand-edited bookmark URL can hold a range with the wrong number of values.
    # The app must still load, and those sliders fall back to their defaults.
    query = urlencode(
        {
            "days": json.dumps(["2026-06-15"]),
            "moments": json.dumps(["2026-06-15T12:34:56", "2026-07-01", "2026-08-01"]),
            "numbers": json.dumps([6]),
            "day": json.dumps("2026-06-15"),
        }
    )
    with run_shiny_app(Path(__file__).with_name("app.py"), wait_for_start=True) as app:
        page.goto(f"{app.url}?_inputs_&{query}")
        InputSliderRange(page, "days").expect_value(("2026-02-01", "2026-03-01"))
        InputSliderRange(page, "moments").expect_value(
            ("2026-02-01 00:00:00", "2026-03-01 00:00:00")
        )
        InputSliderRange(page, "numbers").expect_value(("2", "3"))
        InputSlider(page, "day").expect_value("2026-06-15")
