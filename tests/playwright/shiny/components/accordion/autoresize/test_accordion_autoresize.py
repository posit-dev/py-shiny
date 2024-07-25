from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.playwright.expect import expect_not_to_have_style, expect_to_have_style
from shiny.run import ShinyAppProc


def test_accordion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    text = controller.OutputCode(page, "text")
    tab = controller.NavsetTab(page, "tab")

    test_text_area = controller.InputTextArea(page, "test_text_area")
    test_text_area_w_rows = controller.InputTextArea(page, "test_text_area2")

    text.expect_value("Loaded")

    # Make sure the `rows` is respected
    test_text_area_w_rows.expect_rows("4")
    # Make sure the placeholder row value of `0` is set
    test_text_area.expect_rows("0")

    tab.set("Text Area")

    textareatext = (
        "How can this UI code be tweaked\n"
        "such that this multiline string\n"
        "makes the Text Area Input object\n"
        "resize itself event though it lives\n"
        "inside an Accordion element?"
    )

    test_text_area.expect_autoresize(True)
    test_text_area.expect_value(textareatext)

    expect_to_have_style(test_text_area.loc, "height", "125px")
    expect_not_to_have_style(test_text_area_w_rows.loc, "height")

    # Make sure the placeholder row value of `1` is set
    test_text_area.expect_rows("1")
    # Make sure the `rows` is respected
    test_text_area_w_rows.expect_rows("4")

    # Reset the text area to a single row and make sure the area shrink to appropriate size
    test_text_area.set("single row")
    test_text_area_w_rows.set("single row")

    # 1 row
    expect_to_have_style(test_text_area.loc, "height", "35px")
    # 4 rows
    expect_to_have_style(test_text_area_w_rows.loc, "height", "102px")
