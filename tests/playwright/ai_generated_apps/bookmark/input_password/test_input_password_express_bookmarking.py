from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_text_input_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test text input
    text_input = controller.InputText(page, "basic_text")
    text_output = controller.OutputText(page, "basic_text_value")

    mod_input_txt = controller.InputText(page, "first-module_text")
    mod_output_txt = controller.OutputText(page, "first-text_value")

    # Test password input
    password_input = controller.InputPassword(page, "basic")
    password_output = controller.OutputText(page, "basic_password_value")

    mod_input_password = controller.InputPassword(page, "first-module_password")
    mod_output_password = controller.OutputText(page, "first-password_text")

    # Check initial values
    text_output.expect_value("Text input value:")
    mod_output_txt.expect_value("Text input value:")
    password_output.expect_value("Password value:")
    mod_output_password.expect_value("Password value:")

    # Set text input values
    text_input.set("Hello world")
    text_output.expect_value("Text input value: Hello world")

    mod_input_txt.set("Hello Miami")
    mod_output_txt.expect_value("Text input value: Hello Miami")

    # Set password input values
    password_input.set("password")
    password_output.expect_value("Password value: password")

    mod_input_password.set("password")
    mod_output_password.expect_value("Password value: password")

    # click bookmark button
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    page.reload()

    # Check if the values are retained after reloading the page
    text_output.expect_value("Text input value: Hello world")
    mod_output_txt.expect_value("Text input value: Hello Miami")
    password_output.expect_value("Password value:")
    mod_output_password.expect_value("Password value:")
