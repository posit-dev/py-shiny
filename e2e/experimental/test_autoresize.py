from conftest import ShinyAppProc, x_create_doc_example_fixture
from controls import InputTextArea, OutputTextVerbatim
from playwright.sync_api import Page

app = x_create_doc_example_fixture("input_text_area")


def test_autoresize(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    input_area = InputTextArea(page, "caption")
    input_area.expect_height(None)
    input_area.expect_width(None)
    input_area.set("test value")
    OutputTextVerbatim(page, "value").expect_value("test value")
    for _ in range(6):
        input_area.loc.press("Enter")
    input_area.loc.type("end value")
    OutputTextVerbatim(page, "value").expect_value("test value\n\n\n\n\n\nend value")
    # uncomment after bug is fixed -
    # input_area.expect_rows("6")
