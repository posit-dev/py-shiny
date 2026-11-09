from urllib.parse import urlencode

import pytest
from playwright.sync_api import Page

from shiny.playwright.controller import InputSelectize, OutputCode
from shiny.run import ShinyAppProc


@pytest.mark.parametrize(
    "saved,selected",
    [
        pytest.param('["Week"]', ["Week"], id="selected"),
        pytest.param("null", [], id="null"),
        pytest.param("[]", [], id="empty"),
    ],
)
def test_bookmark_selectize_preserves_available_choices(
    page: Page, local_app: ShinyAppProc, saved: str, selected: list[str]
) -> None:
    query = urlencode({"single": '"Week"', "multiple": saved})
    page.goto(local_app.url + "?_inputs_&" + query)

    single = InputSelectize(page, "single")
    multiple = InputSelectize(page, "multiple")
    single.expect_selected(["Week"])
    multiple.expect_selected(selected)
    single.expect_choices(["Day", "Week", "Month"])
    multiple.expect_choices(
        [choice for choice in ["Day", "Week", "Month"] if choice not in selected]
    )
    OutputCode(page, "single_value").expect_value("Week")
    OutputCode(page, "multiple_value").expect_value("('Week',)" if selected else "()")

    # Options omitted from the bookmark must remain usable after restoration.
    single.set("Month")
    multiple.set(["Month"])
    single.expect_selected(["Month"])
    multiple.expect_selected(["Month"])
    OutputCode(page, "single_value").expect_value("Month")
    OutputCode(page, "multiple_value").expect_value("('Month',)")
