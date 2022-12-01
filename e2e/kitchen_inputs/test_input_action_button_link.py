import re

from conftest import ShinyAppProc, create_doc_example_fixture
from playground import InputActionButton, InputActionLink
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("update_action_button")


def test_input_action_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    button2 = InputActionButton(page, "goButton2")
    expect(button2.loc).to_have_text("🤩 Go 2")
    button2.expect_label_to_have_text("🤩 Go 2")
    button2.expect_width_to_have_value(None)

    assert button2.value_label() is not None, "label is not None"
    assert (
        re.search(r"🤩\s+Go 2", button2.value_label()) is not None
    ), "label is '🤩 Go 2'"
    assert button2.value_width() is None, "width style is None by default"

    link = InputActionLink(page, "goLink")
    link.expect_label_to_have_text("Go Link")

    assert link.value_label() == "Go Link", "label is 'Go Link'"

    button1 = InputActionButton(page, "goButton")
    button1.expect_label_to_have_text("Go")
    button3 = InputActionButton(page, "goButton3")
    button3.expect_label_to_have_text("Go 3")

    InputActionButton(page, "update").click()

    button1.expect_label_to_have_text("📅 New label")
    button2.expect_label_to_have_text("🤩 Go 2")
    button3.expect_label_to_have_text("New label 3")
    link.expect_label_to_have_text("🔗 New link label")
