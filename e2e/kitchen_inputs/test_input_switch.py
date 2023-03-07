from conftest import ShinyAppProc, create_doc_example_fixture
from playground import InputSwitch, OutputUi
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("input_switch")


def test_input_switch_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    somevalue = InputSwitch(page, "somevalue")
    somevalue.expect_label_to_have_text

    expect(somevalue.loc_label).to_have_text("Some value")
    somevalue.expect_label_to_have_text("Some value")

    somevalue.expect_to_be_checked(False)
    somevalue.expect_width_to_have_value(None)

    expect(OutputUi(page, "value").loc).to_have_text("False")

    somevalue.set(True)

    somevalue.expect_to_be_checked(True)

    somevalue.toggle()
    somevalue.expect_to_be_checked(False)

    somevalue.toggle()
    somevalue.expect_to_be_checked(True)

    expect(OutputUi(page, "value").loc).to_have_text("True")
