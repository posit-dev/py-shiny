from conftest import ShinyAppProc
from controls import Popover
from playwright.sync_api import Page


def test_popover(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    popover = Popover(page, "popover_id")
    popover.set(True)
    popover.expect_active()
    popover.expect_body("A message")
