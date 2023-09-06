from conftest import ShinyAppProc
from controls import InputActionButton, Popover
from playwright.sync_api import Page

# def get_popover_id(page: Page) -> str | None:
#     return page.locator(
#         "div > bslib-popover#{id} > button[data-bs-toggle='popover']"
#     ).get_attribute("aria-describedby")


def test_popover(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    input_action_button = InputActionButton(page, "btn_w_popover")
    input_action_button.click()
    popover = Popover(page, "popover_id")
    popover.expect_active()
    popover.expect_body("A message")
