from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_checkbox_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default = controller.InputCheckbox(page, "default")
    default.expect_label("Basic Checkbox")
    default.expect_checked(False)

    value = controller.InputCheckbox(page, "value")
    value.expect_checked(True)

    width = controller.InputCheckbox(page, "width")
    width.expect_width("10px")
