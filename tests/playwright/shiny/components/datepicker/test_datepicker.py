from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_dynamic_navs(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Check the initial state of the date picker where value = max
    date1 = controller.InputDate(page, "start_date_picker")
    date1.expect_value("14.11.2011")
