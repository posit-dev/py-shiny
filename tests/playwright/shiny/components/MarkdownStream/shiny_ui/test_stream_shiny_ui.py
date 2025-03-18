from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_validate_stream_shiny_ui(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    TIMEOUT = 30 * 1000

    stream = page.locator("#stream")
    expect(stream).to_be_visible(timeout=TIMEOUT)

    select = controller.InputSelect(page, "select")
    expect(select.loc).to_be_visible(timeout=TIMEOUT)

    toggle = controller.InputSwitch(page, "toggle")
    expect(toggle.loc).to_be_visible(timeout=TIMEOUT)

    insert_input = controller.InputActionButton(page, "insert_input")
    expect(insert_input.loc).to_be_visible(timeout=TIMEOUT)

    input_vals = controller.OutputCode(page, "input_vals")
    expect(input_vals.loc).to_be_visible(timeout=TIMEOUT)

    dynamic_input_output = controller.OutputCode(page, "dynamic_input_output")
    expect(dynamic_input_output.loc).to_be_visible(timeout=TIMEOUT)

    # Test initial state
    input_vals.expect_value("Selected: a Toggled: False")

    # State changes
    select.set("b")
    input_vals.expect_value("Selected: b Toggled: False")
    toggle.set(True)
    input_vals.expect_value("Selected: b Toggled: True")

    # Clicking should insert text input
    insert_input.click()
    text = controller.InputText(page, "text")
    expect(text.loc).to_be_visible(timeout=TIMEOUT)

    # Check the dynamic input value can be read
    text.set("Some value")
    dynamic_input_output.expect_value("Dynamic input value: 'Some value'")
