from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("output_code")


def test_output_code_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    source = controller.InputTextArea(page, "source")
    code_default = controller.OutputCode(page, "code_default")
    code_no_placeholder = controller.OutputCode(page, "code_no_placeholder")

    source.set("")

    code_default.expect_value("")
    code_default.expect_has_placeholder(True)

    code_no_placeholder.expect_value("")
    code_no_placeholder.expect_has_placeholder(False)

    new_value = "print('testing output_code')\nfor i in range(2):\n    print(i)"
    source.set(new_value)

    code_default.expect_value(new_value)
    code_no_placeholder.expect_value(new_value)
