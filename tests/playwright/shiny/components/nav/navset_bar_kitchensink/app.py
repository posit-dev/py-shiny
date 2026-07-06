from typing import Any

from shiny.express import expressify, ui


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


@expressify
def navset_bar_panel(tab_name: str, navset_args: dict[str, Any]) -> None:
    with ui.nav_panel(tab_name):
        with ui.card(style="position: relative;"):
            navset_kwargs = navset_args.copy()
            navbar_options_keys = (
                "position",
                "bg",
                "theme",
                "inverse",
                "collapsible",
                "underline",
            )
            navbar_options_kwargs: dict[str, Any] = {}
            for key in navbar_options_keys:
                if key not in navset_kwargs:
                    continue

                value = navset_kwargs.pop(key)

                if key == "inverse":
                    navbar_options_kwargs["theme"] = "dark" if value else "light"
                else:
                    navbar_options_kwargs[key] = value
            if navbar_options_kwargs:
                navset_kwargs["navbar_options"] = ui.navbar_options(
                    **navbar_options_kwargs
                )

            with ui.navset_bar(**navset_kwargs):
                with ui.nav_panel("A"):
                    "Panel A content"

                with ui.nav_panel("B"):
                    "Panel B content"


# Add extra spaces so that the navset_tab is below the fixed-top navset_bar
ui.br()
ui.br()
ui.br()
ui.br()

with ui.navset_tab(id="navsets_collection"):
    for tab_name, navset_args in navset_bar_infos:
        navset_bar_panel(tab_name, navset_args)
