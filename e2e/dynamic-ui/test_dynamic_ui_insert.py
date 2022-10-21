from conftest import ShinyAppProc
from playwright.sync_api import Page, expect
from controls import SliderInput, ActionButton, PlotOutput, TextOutputVerbatim

def test_dynamic_ui_insert(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    slider = SliderInput(page, "N")
    expect(slider.loc).to_be_visible()

    txt_output = TextOutputVerbatim(page, "txt")

    expect(txt_output.loc).to_contain_text("N*2 is 40")

    plot = PlotOutput(page, "plot")
    expect(plot.loc).to_be_visible()

    # Insert UI
    button = ActionButton(page, "btn")
    button.loc.click()

    html_output = page.locator("#thanks")
    expect(html_output).to_be_visible()
    expect(html_output).to_have_text("Thanks for clicking!")

    # Remove UI
    button = ActionButton(page, "btn")
    button.loc.click()
    expect(html_output).not_to_be_visible()
