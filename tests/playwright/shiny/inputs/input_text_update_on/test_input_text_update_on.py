# test_input_text_update_on.py

import time

from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def click_action_button(page: Page, x: controller.InputActionButton):
    """Click the button without moving focus (changes input, doesn't change value)"""
    page.evaluate("([id]) => document.getElementById(id).click()", [x.id])


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


def test_text_area_input_change(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    input = controller.InputTextArea(page, "change-txtarea")
    output = controller.OutputTextVerbatim(page, "change-value_txtarea")
    update = controller.InputActionButton(page, "change-update_text_area")

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
    the_value = "The old oak tree whispered secrets to the wind.\nClouds painted shadows on the mountain peaks."
    output.expect_value(the_value)


def test_text_area_input_blur(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    input = controller.InputTextArea(page, "blur-txtarea")
    output = controller.OutputTextVerbatim(page, "blur-value_txtarea")
    update = controller.InputActionButton(page, "blur-update_text_area")

    the_value = "Hello"
    input.set(the_value)
    input.loc.blur()
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

    input.loc.press("Enter")
    output.expect_value(the_value)  # doesn't change on Enter for textAreaInput

    the_value = "Hello, world!"
    input.loc.press("Control+Enter")
    output.expect_value(the_value)  # changes after Control+Enter

    click_action_button(page, update)
    input.expect_value(
        "The old oak tree whispered secrets to the wind.\nClouds painted shadows on the mountain peaks."
    )
    output.expect_value(the_value)

    click_action_button(page, update)
    input.expect_value(
        "Clouds painted shadows on the mountain peaks.\nStars danced across the midnight canvas."
    )
    output.expect_value(the_value)

    the_value = "Clouds painted shadows on the mountain peaks.\nStars danced across the midnight canvas."
    input.loc.press("Control+Enter")
    output.expect_value(the_value)


def test_numeric_input_change(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    input = controller.InputNumeric(page, "change-num")
    output = controller.OutputTextVerbatim(page, "change-value_num")
    update = controller.InputActionButton(page, "change-update_number")

    the_value = "10"
    input.set(the_value)
    output.expect_value(the_value)

    input.loc.press("ArrowUp")
    the_value = "11"
    output.expect_value(the_value)

    input.loc.press("ArrowDown")
    input.loc.press("ArrowDown")
    the_value = "9"
    output.expect_value(the_value)

    click_action_button(page, update)
    the_value = "42"
    output.expect_value(the_value)


def test_numeric_input_blur(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    input = controller.InputNumeric(page, "blur-num")
    output = controller.OutputTextVerbatim(page, "blur-value_num")
    update = controller.InputActionButton(page, "blur-update_number")

    the_value = "10"
    input.set(the_value)
    input.loc.blur()
    output.expect_value(the_value)

    input.loc.focus()
    input.loc.press("ArrowUp")
    output.expect_value(the_value)  # has not changed yet!

    input.loc.blur()
    the_value = "11"
    output.expect_value(the_value)  # changes on blur

    input.loc.focus()
    input.loc.press("ArrowDown")
    input.loc.press("ArrowDown")
    output.expect_value(the_value)  # still hasn't changed yet

    input.loc.press("Enter")
    the_value = "9"
    output.expect_value(the_value)  # changes after Enter

    click_action_button(page, update)
    input.expect_value("42")
    output.expect_value(the_value)

    click_action_button(page, update)
    input.expect_value("3.14159")
    output.expect_value(the_value)

    the_value = "3.14159"
    input.loc.press("Enter")
    output.expect_value(the_value)


def test_password_input_change(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    input = controller.InputPassword(page, "change-pwd")
    output = controller.OutputTextVerbatim(page, "change-value_pwd")
    update = controller.InputActionButton(page, "change-update_pwd")

    the_value = "H3ll0"
    input.set(the_value)
    output.expect_value(the_value)

    input.loc.press("End")
    input.loc.type("_w0r1d")

    time.sleep(0.5)
    the_value = "H3ll0_w0r1d"
    output.expect_value(the_value)
    expect(input.loc).to_be_focused()

    click_action_button(page, update)
    the_value = "Tr0ub4dor&3"
    output.expect_value(the_value)


def test_password_input_blur(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    input = controller.InputPassword(page, "blur-pwd")
    output = controller.OutputTextVerbatim(page, "blur-value_pwd")
    update = controller.InputActionButton(page, "blur-update_pwd")

    the_value = "H3ll0"
    input.set(the_value)
    input.loc.blur()
    output.expect_value(the_value)

    input.loc.focus()
    input.loc.press("End")
    input.loc.type("_w0r1d")

    output.expect_value(the_value)  # has not changed yet!

    the_value = "H3ll0_w0r1d"
    input.loc.blur()
    output.expect_value(the_value)  # changes on blur

    input.loc.focus()
    input.loc.press("End")
    input.loc.type("!")
    output.expect_value(the_value)  # still hasn't changed yet

    the_value = "H3ll0_w0r1d!"
    input.loc.press("Enter")
    output.expect_value(the_value)  # changes after Enter

    click_action_button(page, update)
    input.expect_value("Tr0ub4dor&3")
    output.expect_value(the_value)

    click_action_button(page, update)
    input.expect_value("P@ssw0rd123!")
    output.expect_value(the_value)

    the_value = "P@ssw0rd123!"
    input.loc.press("Enter")
    output.expect_value(the_value)
