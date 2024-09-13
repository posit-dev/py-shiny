from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_page_navbar_fixed_bottom_inverse_bg(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    page_navbar_fixed_bottom_inverse_bg = controller.PageNavbar(
        page, "page_fixed_bottom_inverse_bg"
    )
    page_navbar_fixed_bottom_inverse_bg.expect_position("fixed-bottom")
    page_navbar_fixed_bottom_inverse_bg.expect_inverse(value=True)
    page_navbar_fixed_bottom_inverse_bg.expect_bg("dodgerBlue")
