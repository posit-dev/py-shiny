from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_text_input_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test text input
    text_input = controller.InputText(page, "demo_text")
    text_output = controller.OutputText(page, "current_value")

    # Test initial state
    text_input.expect_label("Demo Text Input")
    text_input.expect_value("Initial value")
    text_input.expect_width("300px")
    text_input.expect_placeholder("Enter text here")
    text_input.expect_autocomplete("off")
    text_input.expect_spellcheck("true")
    text_output.expect_value("Current value: Initial value")

    # Test setting new value
    text_input.set("New test value")
    text_output.expect_value("Current value: New test value")

    # Test empty value
    text_input.set("")
    text_output.expect_value("Current value: ")
