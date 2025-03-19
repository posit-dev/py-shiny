from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_text_area_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test text input
    text_input = controller.InputTextArea(page, "basic")
    text_output = controller.OutputText(page, "basic_text")

    mod_input_txt = controller.InputTextArea(page, "first-module_text_area")
    mod_output_txt = controller.OutputText(page, "first-text_area_text")

    text_output.expect_value("Text area value:")
    mod_output_txt.expect_value("Text area value:")

    text_input.set("Hello world")
    text_output.expect_value("Text area value: Hello world")

    mod_input_txt.set("Hello Miami")
    mod_output_txt.expect_value("Text area value: Hello Miami")

    # click bookmark button
    page.get_by_role("button", name="🔗 Bookmark...").click()

    text_input.set("Hello again")
    text_output.expect_value("Text area value: Hello again")
    mod_input_txt.set("Hello again Miami")
    mod_output_txt.expect_value("Text area value: Hello again Miami")

    # reload pagw
    page.reload()

    text_output.expect_value("Text area value: Hello world")
    mod_output_txt.expect_value("Text area value: Hello Miami")
