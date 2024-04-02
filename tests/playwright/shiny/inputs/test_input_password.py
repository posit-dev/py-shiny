from conftest import ShinyAppProc, create_doc_example_core_fixture
from controls import InputActionButton, InputPassword, OutputTextVerbatim
from playwright.sync_api import Page, expect

app = create_doc_example_core_fixture("input_password")


def test_input_password_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    password = InputPassword(page, "password")
    password.expect.to_have_value("")
    expect(password.loc).to_have_value("")

    expect(password.loc_label).to_have_text("Password:")

    password.expect_label("Password:")
    password.expect_value("")
    password.expect_width(None)
    password.expect_placeholder(None)

    password_value = "test password"
    password.set(password_value)

    InputActionButton(page, "go").click()
    password.expect_value(password_value)
    OutputTextVerbatim(page, "value").expect.to_have_text(password_value)
