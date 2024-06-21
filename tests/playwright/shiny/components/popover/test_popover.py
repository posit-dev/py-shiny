from playwright.sync_api import Page

from shiny.playwright.controls import Popover
from shiny.run import ShinyAppProc


def test_popover(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    popover = Popover(page, "popover_id")
    popover.expect_active(False)
    popover.set(True)
    popover.expect_active(True)
    popover.expect_body("A message")
    popover.expect_placement("bottom")
    popover.set(False)
    popover.expect_active(False)
