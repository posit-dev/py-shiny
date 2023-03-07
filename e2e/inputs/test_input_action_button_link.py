from conftest import ShinyAppProc, create_doc_example_fixture
from controls import InputActionButton, InputActionLink
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("update_action_button")


def test_input_action_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    button2 = InputActionButton(page, "goButton2")
    expect(button2.loc).to_have_text("🤩 Go 2")
    button2.expect_label("🤩 Go 2")
    button2.expect_width(None)

    link = InputActionLink(page, "goLink")
    link.expect_label("Go Link")

    button1 = InputActionButton(page, "goButton")
    button1.expect_label("Go")
    button3 = InputActionButton(page, "goButton3")
    button3.expect_label("Go 3")

    InputActionButton(page, "update").click()

    button1.expect_label("📅 New label")
    button2.expect_label("🤩 Go 2")
    button3.expect_label("New label 3")
    link.expect_label("🔗 New link label")
