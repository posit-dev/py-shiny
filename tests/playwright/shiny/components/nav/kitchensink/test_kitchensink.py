from playwright.sync_api import Page

from shiny.playwright import controller
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


def test_navset_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Update the page size to be wider
    page.set_viewport_size({"width": 1500, "height": 800})

    # for cases across all navsets
    for navset_name, default_content, selected_content in navsets:
        navset = controller.NavPanel(page, "navsets_collection", navset_name)
        navset.click()

        navset_default = getattr(
            controller, f"{navset_name.replace('_', ' ').title().replace(' ', '')}"
        )(page, f"{navset_name}_default")
        navset_default._expect_content_text(default_content)
        navset_default.expect_value(f"{navset_name}_a")

        navset_selected = getattr(
            controller, f"{navset_name.replace('_', ' ').title().replace(' ', '')}"
        )(page, f"{navset_name}_selected")
        navset_selected._expect_content_text(selected_content)
        navset_selected.expect_value(f"{navset_name}_b")

        navset_with_header_footer = getattr(
            controller, f"{navset_name.replace('_', ' ').title().replace(' ', '')}"
        )(page, f"{navset_name}_with_header_footer")
        # TODO-karan: uncomment test to check for header & footer content once class is added
        # navset_with_header_footer.expect_header(f"{navset_name}_with_header_footer header")
        # navset_with_header_footer.expect_footer(f"{navset_name}_with_header_footer footer")
        if navset_name.startswith("navset_card"):
            navset_with_header_footer.expect_title(f"{navset_name}_with_header_footer")

        # check sidebar which has been enabled just for navset_card_underline
        if navset_name == "navset_card_underline":
            navset_card_underline_with_sidebar = getattr(
                controller, f"{navset_name.replace('_', ' ').title().replace(' ', '')}"
            )(page, f"{navset_name}_with_sidebar")
            navset_card_underline_with_sidebar.expect_sidebar(True)
