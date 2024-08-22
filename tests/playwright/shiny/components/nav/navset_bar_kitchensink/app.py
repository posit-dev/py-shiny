from shiny.express import ui


def navset_sidebar():
    from shiny import ui as core_ui

    return core_ui.sidebar(core_ui.markdown("Sidebar content"))


navset_bars = [
    {
        "title": "navset_bar_fixed_top_position_selected",
        "id": "navset_bar_fixed_top_position_selected",
        "position": "fixed-top",
        "selected": "B",
    },
    {
        "title": "navset_bar_header_footer_fixed_bottom_position",
        "id": "navset_bar_header_footer_fixed_bottom_position",
        "header": "Header",
        "footer": "Footer",
        "position": "fixed-bottom",
    },
    {
        "title": "navset_bar_with_sidebar_collapsible_bg_inverse",
        "id": "navset_bar_with_sidebar_collapsible_bg_inverse",
        "sidebar": navset_sidebar(),
        "collapsible": True,
        "bg": "DodgerBlue",
        "inverse": True,
        "position": "sticky-top",
    },
    {
        "title": "navset_bar_collapsible_underline_fixed_gap",
        "id": "navset_bar_collapsible_underline_fixed_gap",
        "collapsible": False,
        "underline": True,
        "fluid": False,
        "gap": "50px",
    },
]

for navset_bar in navset_bars:
    with ui.navset_bar(**navset_bar):  # pyright: ignore[reportArgumentType]
        with ui.nav_panel("A"):
            "Panel A content"

        with ui.nav_panel("B"):
            "Panel B content"
