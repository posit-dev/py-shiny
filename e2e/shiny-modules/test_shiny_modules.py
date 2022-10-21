from conftest import ShinyAppProc, create_doc_example_fixture
from playwright.sync_api import Page
from controls import ActionButton, TextOutput

shinymodules_app = create_doc_example_fixture("Module")


def test_shiny_modules(page: Page, shinymodules_app: ShinyAppProc):
    page.goto(shinymodules_app.url)

    counter1 = ActionButton(page, "counter1-button")
    # Click counter1 button one time and verify the number of clicks in text output
    counter1.loc.click()
    txt_output1 = TextOutput(page, "counter1-out")
    txt_output1.expect.to_have_text("Click count is 1")

    counter2 = ActionButton(page, "counter2-button")
    # Click counter2 button two times and verify the number of clicks in text output
    [counter2.loc.click() for x in range(2)]
    #counter2.loc.dblclick() #TODO: Playwright double click doesn't work
    txt_output2 = TextOutput(page, "counter2-out")
    txt_output2.expect.to_have_text("Click count is 2")

    # verify counter1 output text stays the same after after counter2 actions
    txt_output1.expect.to_have_text("Click count is 1")


