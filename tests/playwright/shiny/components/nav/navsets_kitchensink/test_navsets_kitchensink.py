from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.playwright.expect._internal import _expect_nav_to_have_header_footer
from shiny.run import ShinyAppProc

navsets = [
    ("navset_pill", "navset_pill_a content", "navset_pill_b content"),
    ("navset_underline", "navset_underline_a content", "navset_underline_b content"),
    ("navset_tab", "navset_tab_a content", "navset_tab_b content"),
    ("navset_pill_list", "navset_pill_list_a content", "navset_pill_list_b content"),
    ("navset_card_pill", "navset_card_pill_a content", "navset_card_pill_b content"),
    ("navset_card_tab", "navset_card_tab_a content", "navset_card_tab_b content"),
    (
        "navset_card_underline",
        "navset_card_underline_a content",
        "navset_card_underline_b content",
    ),
]


def format_navset_name(navset_name: str) -> str:
    navset_name = navset_name.replace("_", " ")
    navset_name = navset_name.title()
    navset_name = navset_name.replace(" ", "")
    return navset_name


def test_navset_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Update the page size to be wider
    page.set_viewport_size({"width": 1500, "height": 800})

    page_navbar = controller.PageNavbar(page, "navsets_collection")

    # assert window title is same as page title if window title is not explicity set
    page_navbar.expect_window_title("Navsets kitchensink App")

    # for cases across all navsets
    for navset_name, default_content, selected_content in navsets:
        navset = controller.NavPanel(page, "navsets_collection", navset_name)
        navset.click()

        navset_default = getattr(controller, format_navset_name(navset_name))(
            page, f"{navset_name}_default"
        )
        navset_default._expect_content_text(default_content)
        navset_default.expect_value(f"{navset_name}_a")

        navset_selected = getattr(controller, format_navset_name(navset_name))(
            page, f"{navset_name}_selected"
        )
        navset_selected._expect_content_text(selected_content)
        navset_selected.expect_value(f"{navset_name}_b")

        navset_with_header_footer = getattr(
            controller, format_navset_name(navset_name)
        )(page, f"{navset_name}_with_header_footer")
        _expect_nav_to_have_header_footer(
            navset_with_header_footer.get_loc_active_content()
            .locator("..")
            .locator(".."),
            f"{navset_name}_header",
            f"{navset_name}_footer",
        )

        # assert header and footer contents
        expect(page.locator(f"#{navset_name}_header")).to_have_text(
            f"{navset_name}_with_header_footer header"
        )
        expect(page.locator(f"#{navset_name}_footer")).to_have_text(
            f"{navset_name}_with_header_footer footer"
        )
        if navset_name.startswith("navset_card"):
            navset_with_header_footer.expect_title(f"{navset_name}_with_header_footer")

            navset_card_underline_with_sidebar = getattr(
                controller, f"{navset_name.replace('_', ' ').title().replace(' ', '')}"
            )(page, f"{navset_name}_with_sidebar")
            navset_card_underline_with_sidebar.expect_sidebar(True)

        if navset_name in {"navset_card_underline", "navset_card_pill"}:
            navset_card_underline_placement = getattr(
                controller, f"{navset_name.replace('_', ' ').title().replace(' ', '')}"
            )(page, f"{navset_name}_placement")
            navset_card_underline_placement.expect_placement("below")

        if navset_name in {"navset_pill_list"}:
            navset_pill_list_default = controller.NavsetPillList(
                page, f"{navset_name}_default"
            )
            navset_pill_list_default.expect_well(True)
            navset_pill_list_default.expect_widths([4, 8])

            navset_pill_list_with_well = controller.NavsetPillList(
                page, f"{navset_name}_widths_no_well"
            )
            navset_pill_list_with_well.expect_well(False)
            navset_pill_list_with_well.expect_widths([10, 2])
