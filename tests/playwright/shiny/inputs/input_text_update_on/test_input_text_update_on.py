# test_input_text_update_on.py

import time

from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_text_input_change(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    input = controller.InputText(page, "change-txt")
    update = controller.InputActionButton(page, "change-update_text")

    # Test textInput() -- updateOn='change'
    the_value = "Hello"
    input.set(the_value)
    input.expect_value(the_value)

    input.loc.press("End")
    input.loc.type(", world")

    time.sleep(0.5)
    the_value = "Hello, world"
    input.expect_value(the_value)
    expect(input.loc).to_be_focused()

    update.click()
    the_value = "serendipity ephemeral"
    input.expect_value(the_value)


def test_text_input_blur(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    # Test textInput() -- updateOn='blur'
    input = controller.InputText(page, "blur-txt")
    update = controller.InputActionButton(page, "blur-update_text")

    the_value = "Hello"
    input.set(the_value)
    input.expect_value(the_value)

    input.loc.focus()
    input.loc.press("End")
    input.loc.type(", world")

    input.expect_value(the_value)  # has not changed yet!

    the_value = "Hello, world"
    input.loc.blur()
    input.expect_value(the_value)

    input.loc.focus()
    input.loc.press("End")
    input.loc.type("!")
    input.expect_value(the_value)  # still hasn't changed yet
    input.loc.press("Enter")

    the_value = "Hello, world!"
    input.expect_value(the_value)

    page.evaluate(
        "element => element.click()", update.loc
    )  # hopefully doesn't move focus
    input.expect_value(the_value)

    page.evaluate(
        "element => element.click()", update.loc
    )  # hopefully doesn't move focus
    input.expect_value(the_value)

    input.loc.press("Enter")  # now it changes
    the_value = "ephemeral mellifluous"
    input.expect_value(the_value)


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
