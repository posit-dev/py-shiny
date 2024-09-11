from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_navset_bar_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Update the page size to be wider
    page.set_viewport_size({"width": 1500, "height": 800})

    navset_tab = controller.NavsetTab(page, "navsets_collection")
    navset_bar_fixed_top_position_selected = controller.NavsetBar(
        page,
        "navset_bar_fixed_top_position_selected",
    )
    navset_bar_header_footer_fixed_bottom_position = controller.NavsetBar(
        page,
        "navset_bar_header_footer_fixed_bottom_position",
    )
    navset_bar_with_sidebar_collapsible_bg_inverse = controller.NavsetBar(
        page,
        "navset_bar_with_sidebar_collapsible_bg_inverse",
    )
    navset_bar_collapsible_underline_fixed_gap = controller.NavsetBar(
        page,
        "navset_bar_collapsible_underline_fixed_gap",
    )

    navset_tab.set("fixed-top")
    navset_bar_fixed_top_position_selected._expect_content_text("Panel B content")
    navset_bar_fixed_top_position_selected.expect_position("fixed-top")
    navset_bar_fixed_top_position_selected.expect_value("B")

    navset_tab.set("fixed-bottom")
    navset_bar_header_footer_fixed_bottom_position._expect_content_text(
        "Panel A content"
    )
    navset_bar_header_footer_fixed_bottom_position.expect_position("fixed-bottom")
    navset_bar_header_footer_fixed_bottom_position.expect_value("A")

    navset_tab.set("sticky-top")
    navset_bar_with_sidebar_collapsible_bg_inverse._expect_content_text(
        "Panel A content"
    )
    navset_bar_with_sidebar_collapsible_bg_inverse.expect_position("sticky-top")
    navset_bar_with_sidebar_collapsible_bg_inverse.expect_inverse(value=True)
    navset_bar_with_sidebar_collapsible_bg_inverse.expect_bg("DodgerBlue")
    navset_bar_with_sidebar_collapsible_bg_inverse.expect_sidebar(True)
    navset_bar_with_sidebar_collapsible_bg_inverse.expect_fluid(True)

    navset_tab.set("fixed")
    navset_bar_collapsible_underline_fixed_gap._expect_content_text("Panel A content")
    navset_bar_collapsible_underline_fixed_gap.expect_value("A")
    navset_bar_collapsible_underline_fixed_gap.expect_gap("50px")
    navset_bar_collapsible_underline_fixed_gap.expect_fluid(False)
