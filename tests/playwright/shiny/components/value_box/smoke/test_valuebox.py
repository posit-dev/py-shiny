import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@pytest.mark.parametrize("value_box_id", ["valuebox1", "valuebox2"])
def test_valuebox(page: Page, local_app: ShinyAppProc, value_box_id: str) -> None:
    page.goto(local_app.url)

    value_box = controller.ValueBox(page, value_box_id)
    value_box.expect_full_screen(False)
    value_box.set_full_screen(True)
    value_box.expect_full_screen(True)
    if value_box_id == "valuebox1":
        value_box.expect_height(None)
        value_box.expect_title("KPI Title")
        value_box.expect_value("$1 Billion Dollars")
        value_box.expect_body(["30% VS PREVIOUS 30 DAYS"])
    else:
        value_box.expect_height("500px")
        value_box.expect_title("title")
        value_box.expect_value("value")
        value_box.expect_body(["content", "more body"])
        title_tag_name = (
            value_box.loc_title.locator("*")
            .nth(0)
            .evaluate("el => el.tagName.toLowerCase()")
        )
        assert title_tag_name == "p"
    value_box.set_full_screen(False)
    value_box.expect_full_screen(False)
