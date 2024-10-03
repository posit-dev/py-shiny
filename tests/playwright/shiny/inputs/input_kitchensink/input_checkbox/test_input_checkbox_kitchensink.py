from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_checkbox_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default = controller.InputCheckbox(page, "default")
    default.expect_label("Basic Checkbox")
    default.expect_checked(False)
    default_code = controller.OutputCode(page, "default_txt")
    default_code.expect_value("False")
    default.set(True)
    default_code.expect_value("True")
    default.set(False)
    default_code.expect_value("False")

    value = controller.InputCheckbox(page, "value")
    value.expect_checked(True)
    controller.OutputCode(page, "value_txt").expect_value("True")

    width = controller.InputCheckbox(page, "width")
    width.expect_width("10px")
    controller.OutputCode(page, "width_txt").expect_value("False")
