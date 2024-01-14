import pytest
from conftest import ShinyAppProc
from controls import ValueBox
from playwright.sync_api import Page


@pytest.mark.parametrize("value_box_id", ["valuebox1", "valuebox2"])
def test_valuebox(page: Page, local_app: ShinyAppProc, value_box_id: str) -> None:
    page.goto(local_app.url)

    value_box1 = ValueBox(page, "valuebox1")
    # value_box1.expect_height(None); TODO-fix-karan;
    value_box1.expect_title("KPI Title")
    value_box1.expect_value("$1 Billion Dollars")
    value_box1.expect_full_screen(False)
    value_box1.open_full_screen()
    value_box1.expect_full_screen(True)
    value_box1.expect_body(["30% VS PREVIOUS 30 DAYS"])
    value_box1.close_full_screen()
    value_box1.expect_full_screen(False)

    value_box2 = ValueBox(page, "valuebox2")
    # value_box2.expect_height("300px"); TODO-fix-karan;
    value_box2.expect_title("title")
    value_box2.expect_value("value")
    value_box2.expect_full_screen(False)
    value_box2.open_full_screen()
    value_box2.expect_full_screen(True)
    value_box2.expect_body(["content", "more body"])
    value_box2.close_full_screen()
    value_box2.expect_full_screen(False)

    title_tag_name = (
        value_box2.loc_title.locator("*")
        .nth(0)
        .evaluate("el => el.tagName.toLowerCase()")
    )
    assert title_tag_name == "p"
