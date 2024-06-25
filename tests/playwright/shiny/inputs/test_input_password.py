from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("input_password")


def test_input_password_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    password = controller.InputPassword(page, "password")
    password.expect.to_have_value("")
    expect(password.loc).to_have_value("")

    expect(password.loc_label).to_have_text("Password:")

    password.expect_label("Password:")
    password.expect_value("")
    password.expect_width(None)
    password.expect_placeholder(None)

    password_value = "test password"
    password.set(password_value)

    controller.InputActionButton(page, "go").click()
    password.expect_value(password_value)
    controller.OutputTextVerbatim(page, "value").expect.to_have_text(password_value)
