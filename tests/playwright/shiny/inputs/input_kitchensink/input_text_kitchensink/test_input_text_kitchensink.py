from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_text_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default = controller.InputText(page, "default")
    default.expect_label("Default text input")
    default.expect_value("")
    controller.OutputCode(page, "default_txt").expect.to_have_text("")

    placeholder = controller.InputText(page, "placeholder")
    placeholder.expect_placeholder("Enter text here")
    placeholder.expect_value("")
    placeholder.expect_autocomplete("off")

    width = controller.InputText(page, "width")
    width.expect_width("200px")
    width.expect_value("Custom width input")

    autocomplete = controller.InputText(page, "autocomplete")
    autocomplete.expect_autocomplete("on")

    spellcheck = controller.InputText(page, "spellcheck")
    spellcheck.expect_spellcheck("true")
    spellcheck.expect_value("paticular")
    controller.OutputCode(page, "spellcheck_txt").expect.to_have_text("paticular")
    spellcheck.set("Some text")
    spellcheck.expect_value("Some text")
    controller.OutputCode(page, "spellcheck_txt").expect.to_have_text("Some text")
