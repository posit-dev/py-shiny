# See https://github.com/microsoft/playwright-python/issues/1532
# pyright: reportUnknownMemberType=false

from conftest import ShinyAppProc, create_doc_example_fixture
from playground import TextInput, TextVerbatimOutput
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("input_text")


def test_input_text_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # page.set_default_timeout(1000)

    caption = TextInput(page, "caption")
    caption.expect.to_have_value("Data summary")
    expect(caption.loc).to_have_value("Data summary")

    expect(caption.loc_label).to_have_text("Caption:")

    # # Bad approach
    assert caption.value() == "Data summary", "value is 'Data summary'"
    assert caption.value_label() == "Caption:", "value is 'Caption:'"
    assert caption.value_width() is None, "width is None by default"
    assert caption.value_placeholder() is None, "placeholder is None by default"
    assert caption.value_autocomplete() == "off", "autocomplete is 'off' by default"
    assert caption.value_spellcheck() is None, "spellcheck is None by default"

    # # Better approach
    expect(caption.loc_label).to_have_text("Caption:")
    expect(caption.loc).to_have_value("Data summary")
    # Can not test for the absence of something when waiting is involved
    # expect(obs.loc).not_to_have_attribute("width")
    # expect(obs.loc).not_to_have_attribute("placeholder")
    expect(caption.loc).to_have_attribute("autocomplete", "off")
    # expect(obs.loc).not_to_have_attribute("spellcheck")

    # Best approach
    caption.expect_label_to_have_text("Caption:")
    caption.expect_value("Data summary")
    caption.expect_width_to_have_value(None)
    caption.expect_placeholder_to_have_value(None)
    caption.expect_autocomplete_to_have_value("off")
    caption.expect_spellcheck_to_have_value(None)


def test_input_text_typical(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    caption = TextInput(page, "caption")
    caption.expect.to_have_value("Data summary")
    caption.set("test value")
    caption.expect.not_to_have_value("Data summary")
    caption.expect.to_have_value("test value")


def test_input_text_app(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    caption = TextInput(page, "caption")
    caption.expect.to_have_value("Data summary")

    value = TextVerbatimOutput(page, "value")
    value.expect_value("Data summary")

    caption.set("test value")
    caption.expect.to_have_value("test value")
    value.expect_value("test value")
