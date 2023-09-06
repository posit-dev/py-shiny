from conftest import ShinyAppProc
from controls import InputActionButton, Tooltip
from playwright.sync_api import Page

def get_tooltip_id(page: Page) -> str | None:
    return page.locator(
        "div > bslib-tooltip > button[data-bs-toggle='tooltip']"
    ).get_attribute("aria-describedby")


def test_tooltip(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    input_action_button = InputActionButton(page, "btn_w_tooltip")
    input_action_button.click()
    tooltip = Tooltip(page, 'tooltip_id')
    tooltip.expect_active()
    tooltip.expect_body("A message")
