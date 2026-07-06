from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("input_text")


def test_output_text_verbatim_input_text_example(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    caption = controller.InputText(page, "caption")
    verbatim = controller.OutputTextVerbatim(page, "value")

    verbatim.expect_has_placeholder(False)
    verbatim.expect_value("Data summary")

    new_value = "Updated summary 123"
    caption.set(new_value)

    verbatim.expect_value(new_value)
