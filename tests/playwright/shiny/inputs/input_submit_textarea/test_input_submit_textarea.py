from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_submit_textarea_initial_state(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    basic = controller.InputSubmitTextarea(page, "basic")
    basic.expect_label("Enter text")
    basic.expect_placeholder("Type something here...")
    basic.expect_value("Initial value")
    basic.expect_rows("3")
    basic.expect_width("400px")
    basic.expect_data_needs_modifier(True)
    basic.expect_button_label("Submit")

    value_output = controller.OutputCode(page, "basic_value")
    value_output.expect_value("No value submitted yet")


def test_input_submit_textarea_submit_with_button(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    basic = controller.InputSubmitTextarea(page, "basic")
    value_output = controller.OutputCode(page, "basic_value")
    value_output.expect_value("No value submitted yet")

    basic.submit()
    value_output.expect_value("Submitted: Initial value")

    basic.set("New text content")
    basic.expect_value("New text content")
    value_output.expect_value("Submitted: Initial value")

    basic.submit()
    basic.expect_value("")
    value_output.expect_value("Submitted: New text content")


def test_input_submit_textarea_set_and_submit(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    basic = controller.InputSubmitTextarea(page, "basic")
    value_output = controller.OutputCode(page, "basic_value")

    # Set and submit in one call
    basic.set("One-step submission", submit=True)
    basic.expect_value("")
    value_output.expect_value("Submitted: One-step submission")


def test_input_submit_textarea_no_modifier_key(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    no_modifier = controller.InputSubmitTextarea(page, "no_modifier")
    value_output = controller.OutputCode(page, "no_modifier_value")
    no_modifier.expect_data_needs_modifier(False)

    no_modifier.set("Enter key test")
    no_modifier.submit()
    value_output.expect_value("Submitted: Enter key test")


def test_input_submit_textarea_custom_button(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    custom = controller.InputSubmitTextarea(page, "custom_button")
    value_output = controller.OutputCode(page, "custom_button_value")
    custom.expect_button_label("Send")

    custom.set("Custom button test", submit=True)
    value_output.expect_value("Submitted: Custom button test")


def test_input_submit_textarea_update_value(page: Page, local_app: ShinyAppProc):
    """Test updating value from server"""
    page.goto(local_app.url)

    basic = controller.InputSubmitTextarea(page, "basic")
    value_output = controller.OutputCode(page, "basic_value")
    update_btn = controller.InputActionButton(page, "update_value")

    update_btn.click()
    basic.expect_value("Updated value")
    value_output.expect_value("No value submitted yet")

    basic.submit()
    value_output.expect_value("Submitted: Updated value")


def test_input_submit_textarea_update_placeholder(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    basic = controller.InputSubmitTextarea(page, "basic")
    update_btn = controller.InputActionButton(page, "update_placeholder")
    basic.expect_placeholder("Type something here...")

    update_btn.click()
    basic.expect_placeholder("New placeholder text")


def test_input_submit_textarea_programmatic_submit(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    basic = controller.InputSubmitTextarea(page, "basic")
    value_output = controller.OutputCode(page, "basic_value")
    submit_btn = controller.InputActionButton(page, "submit_programmatic")

    basic.set("Programmatically submitted")
    submit_btn.click()
    value_output.expect_value("Submitted: Programmatically submitted")


def test_input_submit_textarea_multiple_submissions(
    page: Page, local_app: ShinyAppProc
):
    page.goto(local_app.url)

    basic = controller.InputSubmitTextarea(page, "basic")
    value_output = controller.OutputCode(page, "basic_value")

    # First submission
    basic.set("First", submit=True)
    value_output.expect_value("Submitted: First")

    # Second submission
    basic.set("Second", submit=True)
    value_output.expect_value("Submitted: Second")

    # Third submission
    basic.set("Third", submit=True)
    value_output.expect_value("Submitted: Third")
