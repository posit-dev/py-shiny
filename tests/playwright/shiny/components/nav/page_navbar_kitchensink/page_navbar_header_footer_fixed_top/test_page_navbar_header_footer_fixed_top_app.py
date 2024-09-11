from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.playwright.expect._internal import _expect_nav_to_have_header_footer
from shiny.run import ShinyAppProc


def test_page_navbar_header_footer_fixed_top(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    page_navbar_header_footer_fixed_top = controller.PageNavbar(
        page, "page_navbar_header_footer_fixed_top"
    )
    page_navbar_header_footer_fixed_top.expect_position("fixed-top")
    _expect_nav_to_have_header_footer(
        page_navbar_header_footer_fixed_top.get_loc_active_content()
        .locator("..")
        .locator(".."),
        "page_navbar_header",
        "page_navbar_footer",
    )

    # assert header and footer contents
    expect(page.locator("#page_navbar_header")).to_have_text("Header")
    expect(page.locator("#page_navbar_footer")).to_have_text("Footer")

    # not working as expected since not showing on app
    page_navbar_header_footer_fixed_top.expect_fluid(False)
