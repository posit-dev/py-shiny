from conftest import ShinyAppProc, create_doc_example_fixture
from controls import InputRadioButtons
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("input_radio_buttons")


def test_input_checkbox_group_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    rb = InputRadioButtons(page, "rb")

    expect(rb.loc_label).to_have_text("Choose one:")
    rb.expect_label("Choose one:")

    rb.expect_choices(["html", "text"])
    rb.expect_choice_labels(["Red Text", "Normal text"])
    rb.expect_selected("html")
    rb.expect_inline(False)

    rb.expect_width(None)

    rb.set("text")

    rb.expect_choices(["html", "text"])
    rb.expect_choice_labels(["Red Text", "Normal text"])
    rb.expect_selected("text")
