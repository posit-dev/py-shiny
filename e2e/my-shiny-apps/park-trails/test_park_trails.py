from conftest import ShinyAppProc
from playwright.sync_api import Page, expect
from controls import SelectizeInput, RadioButtonsInput


def test_park_trails(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    table = page.locator("#result.shiny-html-output")
    expect(table).to_be_visible()

    state = SelectizeInput(page, "state")
    state.select_option("Alaska")

    trail_difficulty = RadioButtonsInput(page, "difficulty")
    trail_difficulty.locate_by_label("Hard").click()

    # Check render or html table ouput
    output = table.locator("tr")
    expect(output).to_have_count(2)

