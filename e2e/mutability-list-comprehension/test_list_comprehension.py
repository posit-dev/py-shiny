from conftest import ShinyAppProc
from playwright.sync_api import Page, expect
from controls import NumericInput, ActionButton


def test_list_comprehension(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Check current state
    num = NumericInput(page, "x")
    num.expect.to_have_value("1")
    output = page.locator("#out")
    expect(output).to_have_text("Raw Values: [] Doubled: []")

    # Add value and verify output list updates
    add_value = ActionButton(page, "submit")
    add_value.loc.click()

    expect(output).to_have_text("Raw Values: [1] Doubled: [2]")

    # Add a new value in the input and check the output
    num.loc.fill("4")
    add_value.loc.click()

    expect(output).to_have_text("Raw Values: [1, 4] Doubled: [2, 8]")




