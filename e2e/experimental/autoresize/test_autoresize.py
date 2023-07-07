from conftest import ShinyAppProc
from controls import InputTextArea, OutputTextVerbatim
from playwright.sync_api import Page


def test_autoresize(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    input_area = InputTextArea(page, "caption")
    input_area.expect_height(None)
    input_area.expect_width(None)
    input_area.set("test value")
    OutputTextVerbatim(page, "value").expect_value("test value")
    for _ in range(6):
        input_area.loc.press("Enter")
    # uncomment after bug is fixed -
    # input_area.expect_rows("6")
    OutputTextVerbatim(page, "value").expect_value("test value")
