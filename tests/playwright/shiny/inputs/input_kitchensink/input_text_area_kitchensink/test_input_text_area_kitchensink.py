from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_text_area_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default = controller.InputTextArea(page, "default")
    default.expect_label("Default text area")
    default.expect_value("")
    controller.OutputCode(page, "default_txt").expect.to_have_text("")

    placeholder = controller.InputTextArea(page, "placeholder")
    placeholder.expect_placeholder("Enter text here")
    placeholder.expect_value("")

    custom_size = controller.InputTextArea(page, "custom_size")
    custom_size.expect_height("150px")
    custom_size.expect_width("300px")

    custom_cols = controller.InputTextArea(page, "cols")
    custom_cols.expect_cols("30")

    custom_rows = controller.InputTextArea(page, "rows")
    custom_rows.expect_rows("5")
    custom_rows.expect_resize("none")

    autocomplete = controller.InputTextArea(page, "autocomplete")
    autocomplete.expect_autocomplete("name")
    autocomplete.expect_resize("horizontal")

    resize = controller.InputTextArea(page, "resize")
    resize.expect_resize("both")
    resize.set("Some text")
    resize.expect_value("Some text")
    controller.OutputCode(page, "resize_txt").expect.to_have_text("Some text")

    spellcheck = controller.InputTextArea(page, "spellcheck")
    spellcheck.expect_spellcheck("true")
    spellcheck.expect_resize("vertical")
