from conftest import ShinyAppProc, x_create_doc_example_fixture
from controls import InputTextArea, OutputTextVerbatim
from playwright.sync_api import Page

app = x_create_doc_example_fixture("input_text_area")

initial_height = "36px"
resize_number = 6


def resized_height(value: int) -> str:
    return str(36 + (24 * value)) + "px"


def test_autoresize(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    input_area = InputTextArea(page, "caption")
    input_area.expect_height(None)
    input_area.expect_width(None)
    input_area.set("test value")
    input_area.expect_height(initial_height)
    OutputTextVerbatim(page, "value").expect_value("test value")
    for _ in range(resize_number):
        input_area.loc.press("Enter")
    input_area.loc.type("end value")
    OutputTextVerbatim(page, "value").expect_value("test value\n\n\n\n\n\nend value")
    input_area.expect_height(resized_height(resize_number))
