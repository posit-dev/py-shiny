from shiny.express import ui


def navset_sidebar():
    from shiny import ui as core_ui

    return core_ui.sidebar(core_ui.markdown("Sidebar content"))


navset_bar_infos = [
    (
        "fixed-top",
        {
            "title": "navset_bar_fixed_top_position_selected",
            "id": "navset_bar_fixed_top_position_selected",
            "position": "fixed-top",
            "selected": "B",
        },
    ),
    (
        "fixed-bottom",
        {
            "title": "navset_bar_header_footer_fixed_bottom_position",
            "id": "navset_bar_header_footer_fixed_bottom_position",
            "header": "Header",
            "footer": "Footer",
            "position": "fixed-bottom",
        },
    ),
    (
        "sticky-top",
        {
            "title": "navset_bar_with_sidebar_collapsible_bg_inverse",
            "id": "navset_bar_with_sidebar_collapsible_bg_inverse",
            "sidebar": navset_sidebar(),
            "collapsible": True,
            "bg": "DodgerBlue",
            "inverse": True,
            "position": "sticky-top",
        },
    ),
    (
        "fixed",
        {
            "title": "navset_bar_collapsible_underline_fixed_gap",
            "id": "navset_bar_collapsible_underline_fixed_gap",
            "collapsible": False,
            "underline": True,
            "fluid": False,
            "gap": "50px",
        },
    ),
]

# Add extra spaces so that the navset_tab is below the fixed-top navset_bar
ui.br()
ui.br()
ui.br()
ui.br()

# TODO-karan; Put each navset_bar into a navpanel within a navset_tab (similar to the navsets_kitchensink app)
with ui.navset_tab(id="navsets_collection"):
    for tab_name, navset_args in navset_bar_infos:
        with ui.nav_panel(tab_name):

            with ui.card(style="position: relative;"):

                with ui.navset_bar(
                    **navset_args  # pyright: ignore[reportArgumentType]
                ):
                    with ui.nav_panel("A"):
                        "Panel A content"

                    with ui.nav_panel("B"):
                        "Panel B content"
