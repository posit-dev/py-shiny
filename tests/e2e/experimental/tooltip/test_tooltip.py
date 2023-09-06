from conftest import ShinyAppProc
from controls import InputActionButton, Tooltip
from playwright.sync_api import Page


def test_tooltip(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    input_action_button = InputActionButton(page, "btn_w_tooltip")
    input_action_button.click()
    tooltip = Tooltip(page, "tooltip_id")
    tooltip.expect_active()
    tooltip.expect_body("A message")
