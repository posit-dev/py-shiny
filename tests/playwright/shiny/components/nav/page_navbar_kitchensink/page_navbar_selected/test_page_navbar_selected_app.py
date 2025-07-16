from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_page_navbar_selected(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    page_navbar_selected = controller.PageNavbar(page, "page_navbar_selected")
    page_navbar_selected.expect_value("View")
    page_navbar_selected._expect_content_text(
        "This page could be used to view the dataset."
    )
