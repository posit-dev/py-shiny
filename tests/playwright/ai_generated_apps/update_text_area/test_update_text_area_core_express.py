from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_update_text_area(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Get the text area controller
    text_area = controller.InputTextArea(page, "textarea")

    new_label = controller.InputText(page, "new_label")
    new_value = controller.InputText(page, "new_value")
    new_placeholder = controller.InputText(page, "new_placeholder")

    show_values = controller.OutputText(page, "show_values")
    show_values.expect_value(
        """
        Current Label: Updated Label
        Current Value: Updated text content
        Current Placeholder: Updated placeholder text
        """
    )

    # Update text are button
    update_button = controller.InputActionButton(page, "update")

    # Test initial state
    text_area.expect_label("Sample Text Area")
    text_area.expect_value("Initial text")
    text_area.expect_placeholder("Enter your text here")

    new_label.expect_label("New Label")
    new_label.expect_value("Updated Label")

    new_placeholder.expect_label("New Placeholder")
    new_placeholder.expect_value("Updated placeholder text")

    new_value.expect_label("New Value")
    new_value.expect_value("Updated text content")

    # Update the text area
    new_label.set("New Label")
    new_value.set("New text content")
    new_placeholder.set("New placeholder text")
    update_button.click()
    text_area.expect_label("New Label")
    text_area.expect_value("New text content")
    text_area.expect_placeholder("New placeholder text")

    # Check the output
    show_values.expect_value(
        """
        Current Label: New Label
        Current Value: New text content
        Current Placeholder: New placeholder text
        """
    )
    text_area.expect_label("New Label")
    text_area.expect_value("New text content")
    text_area.expect_placeholder("New placeholder text")
