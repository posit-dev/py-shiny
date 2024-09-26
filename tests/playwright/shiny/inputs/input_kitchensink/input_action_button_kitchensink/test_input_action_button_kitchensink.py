from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_action_button_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default = controller.InputActionButton(page, "default")
    default.expect_label("Default button")
    controller.OutputCode(page, "default_txt").expect_value("Button clicked 0 times")
    default.click()
    controller.OutputCode(page, "default_txt").expect_value("Button clicked 1 times")

    width = controller.InputActionButton(page, "width")
    width.expect_width("200px")

    disabled = controller.InputActionButton(page, "disabled")
    disabled.expect_disabled()

    
