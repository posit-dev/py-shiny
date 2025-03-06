from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_password_input(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test password input
    pwd = controller.InputPassword(page, "pwd")
    pwd.expect_label("Enter Password")
    pwd.expect_value("default123")
    pwd.expect_width("300px")
    pwd.expect_placeholder("Type your password here")

    # Test password length output
    pwd_length = controller.OutputText(page, "password_length")
    pwd_length.expect_value("Password length: 10 characters")

    # Test masked password output
    pwd_masked = controller.OutputText(page, "password_masked")
    pwd_masked.expect_value("Masked password: **********")

    # Test setting new password
    pwd.set("newpass12")
    pwd.expect_value("newpass12")
    pwd_length.expect_value("Password length: 9 characters")
    pwd_masked.expect_value("Masked password: *********")
