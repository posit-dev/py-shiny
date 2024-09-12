from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_page_navbar_fillable(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    page_navbar_fillable = controller.PageNavbar(page, "page_navbar_fillable")
    page_navbar_fillable._expect_content_text(
        "This page could be used to pick a dataset."
    )
    page_navbar_fillable.expect_fillable(True)
    page_navbar_fillable.expect_gap("300px")
