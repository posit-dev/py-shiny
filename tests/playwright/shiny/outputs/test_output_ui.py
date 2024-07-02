from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("output_ui")


def test_output_ui_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    more_controls = controller.OutputUi(page, "moreControls")

    more_controls.expect_inline(False)

    more_controls.expect_empty(True)
    expect(more_controls.loc).to_have_text("")
    expect(page.locator("#n")).to_have_count(0)
    expect(page.locator("#label")).to_have_count(0)

    controller.InputActionButton(page, "add").click()

    more_controls.expect_empty(False)
    expect(more_controls.loc).not_to_have_text("")
    expect(page.locator("#n")).to_have_count(1)
    expect(page.locator("#label")).to_have_count(1)

    controller.InputSlider(page, "n").expect_value("500")
    controller.InputText(page, "label").expect_value("")
