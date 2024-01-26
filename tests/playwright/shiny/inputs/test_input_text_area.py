import re

from conftest import ShinyAppProc, create_doc_example_core_fixture
from controls import InputTextArea, OutputTextVerbatim
from playwright.sync_api import Locator, Page, expect

app = create_doc_example_core_fixture("input_text_area")

default_txt = "Data summary\nwith\nmultiple\nlines"


def test_input_text_area_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    caption = InputTextArea(page, "caption_regular")
    caption.expect.to_have_value(default_txt)
    expect(caption.loc).to_have_value(default_txt)

    expect(caption.loc_label).to_have_text("Caption:")

    # Better approach
    expect(caption.loc_label).to_have_text("Caption:")
    expect(caption.loc).to_have_value(default_txt)
    expect(caption.loc).not_to_have_attribute("width", re.compile(r".*"))
    expect(caption.loc).not_to_have_attribute("placeholder", re.compile(r".*"))
    expect(caption.loc).not_to_have_attribute("autocomplete", re.compile(r".*"))
    expect(caption.loc).not_to_have_attribute("spellcheck", re.compile(r".*"))

    # Best approach
    caption.expect_label("Caption:")
    caption.expect_value("Data summary\nwith\nmultiple\nlines")
    caption.expect_width(None)
    caption.expect_placeholder(None)
    caption.expect_autocomplete(None)
    caption.expect_spellcheck(None)
    caption.expect_autoresize(False)

    InputTextArea(page, "caption_autoresize").expect_autoresize(True)


def test_input_text_typical(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    caption = InputTextArea(page, "caption_regular")
    caption.expect.to_have_value(default_txt)
    caption.set("test value")
    caption.expect.not_to_have_value(default_txt)
    caption.expect.to_have_value("test value")


def test_input_text_app(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    caption = InputTextArea(page, "caption_regular")
    caption.expect.to_have_value(default_txt)

    value = OutputTextVerbatim(page, "value_regular")
    value.expect_value(default_txt)

    caption.set("test value")
    caption.expect.to_have_value("test value")
    value.expect_value("test value")


resize_number = 6


def get_box_height(locator: Locator) -> float:
    bounding_box = locator.bounding_box()
    if bounding_box is not None:
        return bounding_box["height"]
    else:
        return 0


def test_autoresize(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    input_area = InputTextArea(page, "caption_autoresize")
    output_txt_verbatim = OutputTextVerbatim(page, "value_autoresize")
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
