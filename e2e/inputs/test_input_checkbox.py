from conftest import ShinyAppProc, create_doc_example_fixture
from controls import InputCheckbox
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("input_checkbox")


def test_input_checkbox_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    somevalue = InputCheckbox(page, "somevalue")

    expect(somevalue.loc_label).to_have_text("Some value")
    somevalue.expect_label("Some value")

    somevalue.expect_checked(False)
    somevalue.expect_width(None)

    # TODO-barret test output value

    somevalue.set(True)

    somevalue.expect_checked(True)

    somevalue.toggle()
    somevalue.expect_checked(False)

    somevalue.toggle()
    somevalue.expect_checked(True)

    # TODO-barret test output value
