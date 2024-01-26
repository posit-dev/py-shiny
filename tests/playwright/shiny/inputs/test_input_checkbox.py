from conftest import ShinyAppProc, create_doc_example_core_fixture
from controls import InputCheckbox, OutputUi
from playwright.sync_api import Page, expect

app = create_doc_example_core_fixture("input_checkbox")


def test_input_checkbox_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    somevalue = InputCheckbox(page, "somevalue")
    # use output_ui
    output_txt = OutputUi(page, "value")
    expect(somevalue.loc_label).to_have_text("Some value")
    somevalue.expect_label("Some value")

    somevalue.expect_checked(False)
    somevalue.expect_width(None)

    output_txt.expect_text("False")

    somevalue.set(True)

    somevalue.expect_checked(True)

    somevalue.toggle()
    somevalue.expect_checked(False)

    somevalue.toggle()
    somevalue.expect_checked(True)

    output_txt.expect_text("True")
