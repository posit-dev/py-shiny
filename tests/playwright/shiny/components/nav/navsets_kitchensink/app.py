from typing import Any, Dict

from shiny.express import expressify, ui

ui.page_opts(title="Navsets kitchensink App")


def navset_sidebar():
    from shiny import ui as core_ui

    return core_ui.sidebar(core_ui.markdown("Sidebar content"))


navset_configs: Dict[str, Dict[str, Dict[str, Any]]] = {
    "navset_pill": {
        "default": {},
        "with_header_footer": {
            "header": "navset_pill_with_header_footer header",
            "footer": "navset_pill_with_header_footer footer",
        },
        "selected": {"selected": "navset_pill_b"},
    },
    "navset_underline": {
        "default": {},
        "with_header_footer": {
            "header": "navset_underline_with_header_footer header",
            "footer": "navset_underline_with_header_footer footer",
        },
        "selected": {"selected": "navset_underline_b"},
    },
    "navset_tab": {
        "default": {},
        "with_header_footer": {
            "header": "navset_tab_with_header_footer header",
            "footer": "navset_tab_with_header_footer footer",
        },
        "selected": {"selected": "navset_tab_b"},
    },
    "navset_pill_list": {
        "default": {},
        "with_header_footer": {
            "header": "navset_pill_list_with_header_footer header",
            "footer": "navset_pill_list_with_header_footer footer",
        },
        "selected": {"selected": "navset_pill_list_b"},
        "widths_no_well": {"widths": (10, 2), "well": False},
    },
    "navset_card_pill": {
        "with_header_footer": {
            "title": "navset_card_pill_with_header_footer",
            "header": "navset_card_pill_with_header_footer header",
            "footer": "navset_card_pill_with_header_footer footer",
        },
        "default": {},
        "placement": {"placement": "below"},
        "selected": {"selected": "navset_card_pill_b"},
        "with_sidebar": {"sidebar": navset_sidebar()},
    },
    "navset_card_tab": {
        "with_header_footer": {
            "title": "navset_card_tab_with_header_footer",
            "header": "navset_card_tab_with_header_footer header",
            "footer": "navset_card_tab_with_header_footer footer",
        },
        "default": {},
        "selected": {"selected": "navset_card_tab_b"},
        "with_sidebar": {"sidebar": navset_sidebar()},
    },
    "navset_card_underline": {
        "with_header_footer": {
            "title": "navset_card_underline_with_header_footer",
            "header": "navset_card_underline_with_header_footer header",
            # "header": core_ui.CardItem(
            #     core_ui.TagList(
            #         "navset_card_underline_with_header_footer header1",
            #         core_ui.br(),
            #         "navset_card_underline_with_header_footer header2",
            #     )
            # ),
            "footer": "navset_card_underline_with_header_footer footer",
        },
        "default": {},
        "selected": {"selected": "navset_card_underline_b"},
        "placement": {"placement": "below"},
        "with_sidebar": {"sidebar": navset_sidebar()},
    },
}


@expressify
def create_navset(navset_type: str) -> None:
    navset_function = getattr(ui, navset_type)

    for navset_id, params in navset_configs[navset_type].items():
        with navset_function(id=f"{navset_type}_{navset_id}", **params):
            for suffix in ["a", "b", "c"]:
                with ui.nav_panel(f"{navset_type}_{suffix}"):
                    ui.markdown(f"{navset_type}_{suffix} content")


with ui.navset_tab(id="navsets_collection"):
    for navset_type in navset_configs.keys():
        with ui.nav_panel(navset_type):
            create_navset(navset_type)
