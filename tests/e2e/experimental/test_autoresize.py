from conftest import ShinyAppProc, x_create_doc_example_fixture
from controls import InputTextArea, OutputTextVerbatim
from playwright.sync_api import Locator, Page

app = x_create_doc_example_fixture("input_text_area")

resize_number = 6


def get_box_height(locator: Locator) -> float:
    bounding_box = locator.bounding_box()
    if bounding_box is not None:
        return bounding_box["height"]
    else:
        return 0


def test_autoresize(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    input_area = InputTextArea(page, "caption")
    output_txt_verbatim = OutputTextVerbatim(page, "value")
    input_area.expect_height(None)
    input_area.expect_width(None)
    input_area.set("test value")
    # use bounding box approach since height is dynamic
    initial_height = get_box_height(input_area.loc)
    output_txt_verbatim.expect_value("test value")
    for _ in range(resize_number):
        input_area.loc.press("Enter")
    input_area.loc.type("end value")
    return_txt = "\n" * resize_number
    output_txt_verbatim.expect_value(f"test value{return_txt}end value")
    assert get_box_height(input_area.loc) > initial_height
