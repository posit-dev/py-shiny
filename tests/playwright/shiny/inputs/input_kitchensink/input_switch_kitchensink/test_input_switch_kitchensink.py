from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_switch_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default = controller.InputSwitch(page, "default")
    default.expect_label("Default switch")
    default.expect_checked(False)

    default_code = controller.OutputCode(page, "default_txt")
    default_code.expect_value("False")

    value = controller.InputSwitch(page, "value")
    value.expect_checked(True)
    controller.OutputCode(page, "value_txt").expect_value("True")

    width = controller.InputSwitch(page, "width")
    width.expect_width("200px")
    controller.OutputCode(page, "width_txt").expect_value("False")
    width.set(True)
    width.expect_checked(True)
    controller.OutputCode(page, "width_txt").expect_value("True")
