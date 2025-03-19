from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_radio_buttons_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test radio buttons input
    radio_buttons = controller.InputRadioButtons(page, "basic")
    selection_output = controller.OutputText(page, "basic_text")

    mod_radio_button = controller.InputRadioButtons(page, "first-module_radio")
    mod_selection_output = controller.OutputText(page, "first-radio_text")

    radio_buttons.set("Option 2")
    radio_buttons.expect_selected("Option 2")
    selection_output.expect_value("Radio button value: Option 2")

    mod_radio_button.set("Choice B")
    mod_radio_button.expect_selected("Choice B")
    mod_selection_output.expect_value("Radio button value: Choice B")

    # click bookmark button
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    mod_radio_button.set("Choice C")
    mod_selection_output.expect_value("Radio button value: Choice C")

    radio_buttons.set("Option 3")
    selection_output.expect_value("Radio button value: Option 3")

    # Reload the page to test bookmark
    page.reload()

    radio_buttons.expect_selected("Option 2")
    selection_output.expect_value("Radio button value: Option 2")

    mod_radio_button.expect_selected("Choice B")
    mod_selection_output.expect_value("Radio button value: Choice B")
