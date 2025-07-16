from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("output_text")


def test_output_text_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    txt = controller.InputText(page, "txt")
    text = controller.OutputText(page, "text")
    verb = controller.OutputTextVerbatim(page, "verb")
    verb_no_placeholder = controller.OutputTextVerbatim(page, "verb_no_placeholder")

    txt.set("")  # Reset text

    text.expect_value("")
    text.expect_inline(False)

    verb.expect_value("")
    verb.expect_has_placeholder(True)

    verb_no_placeholder.expect_value("")
    verb_no_placeholder.expect_has_placeholder(False)

    txt_val = "test value 42"
    txt.set(txt_val)

    text.expect_value(txt_val)
    verb.expect_value(txt_val)
    verb_no_placeholder.expect_value(txt_val)
