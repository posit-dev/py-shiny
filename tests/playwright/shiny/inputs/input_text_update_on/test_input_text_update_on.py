# test_input_text_update_on.py

import time

from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def click_action_button(page: Page, x: controller.InputActionButton):
    """Click the button without moving focus (changes input, doesn't change value)"""
    page.evaluate(
        "([id]) => document.getElementById(id).click()", [x.id]
    )

def test_text_input_change(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    input = controller.InputText(page, "change-txt")
    output = controller.OutputTextVerbatim(page, "change-value_txt")
    update = controller.InputActionButton(page, "change-update_text")

    # Test textInput() -- updateOn='change'
    the_value = "Hello"
    input.set(the_value)
    output.expect_value(the_value)

    input.loc.press("End")
    input.loc.type(", world")

    time.sleep(0.5)
    the_value = "Hello, world"
    output.expect_value(the_value)
    expect(input.loc).to_be_focused()

    click_action_button(page, update)
    the_value = "serendipity ephemeral"
    output.expect_value(the_value)


def test_text_input_blur(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    # Test textInput() -- updateOn='blur'
    input = controller.InputText(page, "blur-txt")
    output = controller.OutputTextVerbatim(page, "blur-value_txt")
    update = controller.InputActionButton(page, "blur-update_text")

    the_value = "Hello"
    input.set(the_value)
    output.expect_value(the_value)

    input.loc.focus()
    input.loc.press("End")
    input.loc.type(", world")

    output.expect_value(the_value)  # has not changed yet!

    the_value = "Hello, world"
    input.loc.blur()
    output.expect_value(the_value)  # changes on blur

    input.loc.focus()
    input.loc.press("End")
    input.loc.type("!")
    output.expect_value(the_value)  # still hasn't changed yet

    the_value = "Hello, world!"
    input.loc.press("Enter")
    output.expect_value(the_value)  # changes after Enter

    click_action_button(page, update)
    input.expect_value("serendipity ephemeral")
    output.expect_value(the_value)

    click_action_button(page, update)
    input.expect_value("ephemeral mellifluous")
    output.expect_value(the_value)

    the_value = "ephemeral mellifluous"
    input.loc.press("Enter")  # changes again after Enter
    output.expect_value(the_value)


# Add similar tests for textAreaInput(), numericInput(), and passwordInput()
# following the same pattern as above.


def test_text_area_input_change(page: Page, local_app: ShinyAppProc):
    # Implement test for textAreaInput() with updateOn='change'
    pass


def test_text_area_input_blur(page: Page, local_app: ShinyAppProc):
    # Implement test for textAreaInput() with updateOn='blur'
    pass


def test_numeric_input_change(page: Page, local_app: ShinyAppProc):
    # Implement test for numericInput() with updateOn='change'
    pass


def test_numeric_input_blur(page: Page, local_app: ShinyAppProc):
    # Implement test for numericInput() with updateOn='blur'
    pass


def test_password_input_change(page: Page, local_app: ShinyAppProc):
    # Implement test for passwordInput() with updateOn='change'
    pass


def test_password_input_blur(page: Page, local_app: ShinyAppProc):
    # Implement test for passwordInput() with updateOn='blur'
    pass
