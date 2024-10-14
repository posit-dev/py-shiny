from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("update_action_button")


def test_input_action_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    button2 = controller.InputActionButton(page, "goButton2")
    expect(button2.loc).to_have_text("🤩 Go 2")
    button2.expect_label("🤩 Go 2")
    button2.expect_width(None)

    link = controller.InputActionLink(page, "goLink")
    link.expect_label("Go Link")

    button1 = controller.InputActionButton(page, "goButton")
    button1.expect_label("Go")
    button3 = controller.InputActionButton(page, "goButton3")
    button3.expect_label("Go 3")

    controller.InputActionButton(page, "update").click()

    button1.expect_label("📅 New label")
    button2.expect_label("🤩 Go 2")
    button3.expect_label("New label 3")
    link.expect_label("🔗 New link label")
