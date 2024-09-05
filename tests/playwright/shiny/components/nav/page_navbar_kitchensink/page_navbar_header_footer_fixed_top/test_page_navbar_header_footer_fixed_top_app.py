from playwright.sync_api import Page, expect

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
    parent_loc = page_navbar_header_footer_fixed_top.get_loc_active_content().locator(
        ".."
    )
    # assert the DOM structure for page_navbar with header and footer is preserved
    complicated_parent_loc = parent_loc.locator(
        "xpath=.",
        has=page.locator("#page_navbar_header + .tab-content + #page_navbar_footer"),
    )
    expect(complicated_parent_loc.locator("*")).to_have_count(3)

    # assert header and footer contents
    expect(page.locator("#page_navbar_header")).to_have_text("Header")
    expect(page.locator("#page_navbar_footer")).to_have_text("Footer")

    # not working as expected since not showing on app
    page_navbar_header_footer_fixed_top.expect_layout("fixed")
