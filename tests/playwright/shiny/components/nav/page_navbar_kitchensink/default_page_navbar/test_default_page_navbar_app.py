from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_default_page_navbar(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default_page_navbar = controller.PageNavbar(page, "default_page_navbar")
    default_page_navbar.expect_title("Default Page Navbar")
    default_page_navbar.expect_inverse(value=False)
    default_page_navbar.expect_lang("en")
    default_page_navbar.expect_window_title("Page NavBar title")
    default_page_navbar.expect_fillable_mobile(True)
