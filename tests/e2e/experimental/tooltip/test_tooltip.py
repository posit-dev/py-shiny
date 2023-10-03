from conftest import ShinyAppProc
from controls import Tooltip
from playwright.sync_api import Page


def test_tooltip(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    tooltip = Tooltip(page, "tooltip_id")
    tooltip.expect_active(False)
    tooltip.set(True)
    tooltip.expect_active(True)
    tooltip.expect_body("A message")
    tooltip.expect_placement("right")
    tooltip.set(False)
    tooltip.expect_active(False)
