from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_page_navbar_header_footer_fixed_top(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    page_navbar_header_footer_fixed_top = controller.PageNavbar(
        page, "page_navbar_header_footer_fixed_top"
    )
    page_navbar_header_footer_fixed_top.expect_position("fixed-top")
    # assert the DOM structure for page_navbar with header and footer is preserved
    assert (
        page.locator("#page_navbar_header + .tab-content + #page_navbar_footer").count()
        == 1
    )
    # assert header and footer contents
    assert page.locator("#page_navbar_header").inner_text() == "Header"
    assert page.locator("#page_navbar_footer").inner_text() == "Footer"
    # assert page_navbar_header_footer_fixed_top.expect_layout("fixed") # not working as expected since not showing on app
