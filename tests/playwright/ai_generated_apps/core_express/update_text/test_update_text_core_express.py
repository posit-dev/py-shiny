from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_update_text(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Get controllers for the components with IDs
    text_input = controller.InputText(page, "txt")
    text_output = controller.OutputText(page, "current_value")
    update_all_btn = controller.InputActionButton(page, "update_all")
    update_label_btn = controller.InputActionButton(page, "update_label")
    update_value_btn = controller.InputActionButton(page, "update_value")
    update_placeholder_btn = controller.InputActionButton(page, "update_placeholder")

    # Test initial state
    text_input.expect_label("Original Text")
    text_input.expect_value("Initial value")
    text_input.expect_placeholder("Type something...")
    text_output.expect_value("Current value: Initial value")

    # Test update all parameters
    update_all_btn.click()
    text_input.expect_label("Updated Label")
    text_input.expect_value("Updated Value")
    text_input.expect_placeholder("Updated Placeholder")
    text_output.expect_value("Current value: Updated Value")

    # Test update label only
    update_label_btn.click()
    text_input.expect_label("Label Updated 1 times")
    text_output.expect_value(
        "Current value: Updated Value"
    )  # Value should remain unchanged

    # Test update value only
    update_value_btn.click()
    text_input.expect_value("Value Updated 1 times")
    text_output.expect_value("Current value: Value Updated 1 times")
    text_input.expect_label("Label Updated 1 times")  # Label should remain unchanged

    # Test update placeholder only
    update_placeholder_btn.click()
    text_input.expect_placeholder("Placeholder Updated 1 times")
    text_output.expect_value(
        "Current value: Value Updated 1 times"
    )  # Value should remain unchanged

    # Test manual text input
    text_input.set("User typed value")
    text_output.expect_value("Current value: User typed value")

    # Test multiple updates
    update_label_btn.click()
    text_input.expect_label("Label Updated 2 times")
    update_value_btn.click()
    text_input.expect_value("Value Updated 2 times")
    update_placeholder_btn.click()
    text_input.expect_placeholder("Placeholder Updated 2 times")
