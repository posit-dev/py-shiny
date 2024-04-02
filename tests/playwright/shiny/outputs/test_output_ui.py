from conftest import ShinyAppProc, create_doc_example_core_fixture
from controls import InputActionButton, InputSlider, InputText, OutputUi
from playwright.sync_api import Page, expect

app = create_doc_example_core_fixture("output_ui")


def test_output_ui_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    more_controls = OutputUi(page, "moreControls")

    more_controls.expect_inline(False)

    more_controls.expect_empty(True)
    expect(more_controls.loc).to_have_text("")
    expect(page.locator("#n")).to_have_count(0)
    expect(page.locator("#label")).to_have_count(0)

    InputActionButton(page, "add").click()

    more_controls.expect_empty(False)
    expect(more_controls.loc).not_to_have_text("")
    expect(page.locator("#n")).to_have_count(1)
    expect(page.locator("#label")).to_have_count(1)

    InputSlider(page, "n").expect_value("500")
    InputText(page, "label").expect_value("")
