from conftest import ShinyAppProc
from playground import InputSwitch
from playwright.sync_api import Page, expect


def test_input_switch_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    somevalue = InputSwitch(page, "somevalue")
    somevalue.expect_label_to_have_text

    expect(somevalue.loc_label).to_have_text("Some value")
    somevalue.expect_label_to_have_text("Some value")

    somevalue.expect_to_be_checked(False)
    somevalue.expect_width_to_have_value(None)

    # TODO-barret test output value

    somevalue.set(True)

    somevalue.expect_to_be_checked(True)

    somevalue.toggle()
    somevalue.expect_to_be_checked(False)

    somevalue.toggle()
    somevalue.expect_to_be_checked(True)

    # TODO-barret test output value
