import re

from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("input_text")


def test_input_text_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # page.set_default_timeout(1000)

    caption = controller.InputText(page, "caption")
    caption.expect.to_have_value("Data summary")
    expect(caption.loc).to_have_value("Data summary")

    expect(caption.loc_label).to_have_text("Caption:")

    # Better approach
    expect(caption.loc_label).to_have_text("Caption:")
    expect(caption.loc).to_have_value("Data summary")
    expect(caption.loc).not_to_have_attribute("width", re.compile(r".*"))
    expect(caption.loc).not_to_have_attribute("placeholder", re.compile(r".*"))
    expect(caption.loc).to_have_attribute("autocomplete", "off")
    expect(caption.loc).not_to_have_attribute("spellcheck", re.compile(r".*"))

    # Best approach
    caption.expect_label("Caption:")
    caption.expect_value("Data summary")
    caption.expect_width(None)
    caption.expect_placeholder(None)
    caption.expect_autocomplete("off")
    caption.expect_spellcheck(None)


def test_input_text_typical(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    caption = controller.InputText(page, "caption")
    caption.expect.to_have_value("Data summary")
    caption.set("test value")
    caption.expect.not_to_have_value("Data summary")
    caption.expect.to_have_value("test value")


def test_input_text_app(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    caption = controller.InputText(page, "caption")
    caption.expect.to_have_value("Data summary")

    value = controller.OutputTextVerbatim(page, "value")
    value.expect_value("Data summary")

    caption.set("test value")
    caption.expect.to_have_value("test value")
    value.expect_value("test value")
