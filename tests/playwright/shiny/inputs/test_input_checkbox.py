from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("input_checkbox")


def test_input_checkbox_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    somevalue = controller.InputCheckbox(page, "somevalue")
    # use output_ui
    output_txt = controller.OutputUi(page, "value")
    expect(somevalue.loc_label).to_have_text("Some value")
    somevalue.expect_label("Some value")

    somevalue.expect_checked(False)
    somevalue.expect_width(None)

    output_txt.expect.to_have_text("False")

    somevalue.set(True)

    somevalue.expect_checked(True)

    somevalue.set(False)
    somevalue.expect_checked(False)

    somevalue.set(True)
    somevalue.expect_checked(True)

    output_txt.expect.to_have_text("True")
