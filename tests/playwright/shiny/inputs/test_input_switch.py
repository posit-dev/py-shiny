from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("input_switch")


def test_input_switch_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    somevalue = controller.InputSwitch(page, "somevalue")

    expect(somevalue.loc_label).to_have_text("Some value")
    somevalue.expect_label("Some value")

    somevalue.expect_checked(False)
    somevalue.expect_width(None)

    expect(controller.OutputUi(page, "value").loc).to_have_text("False")

    somevalue.set(True)

    somevalue.expect_checked(True)

    somevalue.set(False)
    somevalue.expect_checked(False)

    somevalue.set(True)
    somevalue.expect_checked(True)

    expect(controller.OutputUi(page, "value").loc).to_have_text("True")
