from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_text_input_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test text input
    text_input = controller.InputText(page, "basic")
    text_output = controller.OutputText(page, "basic_text")

    mod_input_txt = controller.InputText(page, "first-module_text")
    mod_output_txt = controller.OutputText(page, "first-text_text")

    text_output.expect_value("Text input value: Type something here")
    mod_output_txt.expect_value("Text input value: Type something here")

    text_input.set("Hello world")
    text_output.expect_value("Text input value: Hello world")

    mod_input_txt.set("Hello Miami")
    mod_output_txt.expect_value("Text input value: Hello Miami")

    # click bookmark button
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    text_input.set("Hello again")
    text_output.expect_value("Text input value: Hello again")
    mod_input_txt.set("Hello again Miami")
    mod_output_txt.expect_value("Text input value: Hello again Miami")

    # reload pagw
    page.reload()

    text_output.expect_value("Text input value: Hello world")
    mod_output_txt.expect_value("Text input value: Hello Miami")
