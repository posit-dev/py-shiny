from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_page_navbar_sidebar(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    page_navbar_sidebar = controller.PageNavbar(page, "page_navbar_sidebar")
    page_navbar_sidebar.expect_value("Data")
    page_navbar_sidebar._expect_content_text(
        "This page could be used to pick a dataset."
    )
    page_navbar_sidebar.expect_sidebar(True)
