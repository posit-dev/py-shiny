from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_password_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default = controller.InputPassword(page, "default")
    default.expect_label("Default password input")
    default.expect_value("")
    controller.OutputCode(page, "default_txt").expect_value("")

    placeholder = controller.InputPassword(page, "placeholder")
    placeholder.expect_placeholder("Enter password")
    placeholder.expect_value("")

    width = controller.InputPassword(page, "width")
    width.expect_width("200px")

    value = controller.InputPassword(page, "value")
    value.expect_value("secret123")
    controller.OutputCode(page, "value_txt").expect_value("secret123")
    value.set("secret456")
    value.expect_value("secret456")
    controller.OutputCode(page, "value_txt").expect_value("secret456")
