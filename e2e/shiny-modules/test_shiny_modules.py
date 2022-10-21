from conftest import ShinyAppProc, create_example_fixture
from playwright.sync_api import Page
from controls import ActionButton, TextOutput

shinymodules_app = create_example_fixture("moduleapp")


def test_shiny_modules(page: Page, shinymodules_app: ShinyAppProc):
    page.goto(shinymodules_app.url)

    counter1 = ActionButton(page, "counter1-button")
    counter1.loc.click()
    txt_output1 = TextOutput(page, "counter1-out")
    txt_output1.expect.to_have_text("Click count is 1")

    counter2 = ActionButton(page, "counter2_wrapper-counter-button")
    # Click counter2 button two times and verify the number of clicks in text output
    [counter2.loc.click() for x in range(2)] #(counter2.loc.dblclick() #TODO: Playwright double click doesn't work)
    txt_output2 = TextOutput(page, "counter2_wrapper-counter-out")
    txt_output2.expect.to_have_text("Click count is 2")

    counter3 = ActionButton(page, "counter3-button")
    # Click counter2 button two times and verify the number of clicks in text output
    [counter3.loc.click() for x in range(3)]
    txt_output3 = TextOutput(page, "counter3-out")
    txt_output3.expect.to_have_text("Click count is 3")


