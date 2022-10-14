from conftest import ShinyAppProc
from playwright.sync_api import Page, expect
from controls import NumericInput, ActionButton


def test_copy_on_update_app(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Check current state
    num = NumericInput(page, "x")
    num.expect.to_have_value("1")
    output = page.locator("#out")
    expect(output).to_have_text("Values: []")

    # Add value and verify output list updates
    add_value = ActionButton(page, "submit")
    add_value.loc.click()

    expect(output).to_have_text("Values: [1]")

    # Add a new value in the input and check the output
    num.loc.fill("2")
    add_value.loc.click()

    expect(output).to_have_text("Values: [1, 2]")




