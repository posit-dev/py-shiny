from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.playwright.expect import expect_to_have_style
from shiny.run import ShinyAppProc


def test_accordion(page: Page, local_app: ShinyAppProc, is_webkit: bool) -> None:
    page.goto(local_app.url)

    text = controller.OutputCode(page, "text")
    tab = controller.NavsetTab(page, "tab")

    test_text_area = controller.InputTextArea(page, "test_text_area")
    test_text_area_w_rows = controller.InputTextArea(page, "test_text_area2")

    text.expect_value("Loaded")

    # Make sure the `rows` is respected
    test_text_area_w_rows.expect_rows("4")
    # Make sure the placeholder row value of `1` is set
    test_text_area.expect_rows("1")

    tab.set("Text Area")

    test_text_area.expect_autoresize(True)
    test_text_area.expect_value("a\nb\nc\nd\ne")

    if is_webkit:
        # Skip the rest of the test for webkit.
        # Heights are not consistent with chrome and firefox
        return
    expect_to_have_style(test_text_area.loc, "height", "127px")
    expect_to_have_style(test_text_area_w_rows.loc, "height", "127px")

    # Make sure the `rows` is consistent
    test_text_area.expect_rows("1")
    test_text_area_w_rows.expect_rows("4")

    # Reset the text area to a single row and make sure the area shrink to appropriate size
    test_text_area.set("single row")
    test_text_area_w_rows.set("single row")

    # 1 row
    expect_to_have_style(test_text_area.loc, "height", "37px")
    # 4 rows
    expect_to_have_style(test_text_area_w_rows.loc, "height", "104px")
