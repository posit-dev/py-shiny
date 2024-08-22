from typing import Any, Dict

from shiny.express import expressify, ui

ui.page_opts(title="Navsets kitchensink App")

all_content: Dict[str, Dict[str, str]] = {
    "pill": {
        "navset_pill_a": "navset_pill_a content",
        "navset_pill_b": "navset_pill_b content",
        "navset_pill_c": "navset_pill_c content",
    },
    "underline": {
        "navset_underline_a": "navset_underline_a content",
        "navset_underline_b": "navset_underline_b content",
        "navset_underline_c": "navset_underline_c content",
    },
    "tab": {
        "navset_tab_a": "navset_tab_a content",
        "navset_tab_b": "navset_tab_b content",
        "navset_tab_c": "navset_tab_c content",
    },
    "pill_list": {
        "navset_pill_list_a": "navset_pill_list_a content",
        "navset_pill_list_b": "navset_pill_list_b content",
        "navset_pill_list_c": "navset_pill_list_c content",
    },
    "card_pill": {
        "navset_card_pill_a": "navset_card_pill_a content",
        "navset_card_pill_b": "navset_card_pill_b content",
        "navset_card_pill_c": "navset_card_pill_c content",
    },
    "card_tab": {
        "navset_card_tab_a": "navset_card_tab_a content",
        "navset_card_tab_b": "navset_card_tab_b content",
        "navset_card_tab_c": "navset_card_tab_c content",
    },
    "card_underline": {
        "navset_card_underline_a": "navset_card_underline_a content",
        "navset_card_underline_b": "navset_card_underline_b content",
        "navset_card_underline_c": "navset_card_underline_c content",
    },
}


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
            "footer": "navset_card_underline_with_header_footer footer",
        },
        "default": {},
        "selected": {"selected": "navset_card_underline_b"},
        "placement": {"placement": "below"},
        "with_sidebar": {"sidebar": navset_sidebar()},
    },
}


@expressify
def create_navset(navset_type: str, content_type: str) -> None:
    navset_function = getattr(ui, navset_type)
    content = all_content[content_type]

    for navset_id, params in navset_configs[navset_type].items():
        with navset_function(id=f"{navset_type}_{navset_id}", **params):
            for panel_id, panel_content in content.items():
                with ui.nav_panel(panel_id):
                    ui.markdown(panel_content)


with ui.navset_tab(id="navsets_collection"):
    for navset_type, content_type in [
        ("navset_pill", "pill"),
        ("navset_underline", "underline"),
        ("navset_tab", "tab"),
        ("navset_pill_list", "pill_list"),
        ("navset_card_pill", "card_pill"),
        ("navset_card_tab", "card_tab"),
        ("navset_card_underline", "card_underline"),
    ]:
        with ui.nav_panel(navset_type):
            create_navset(navset_type, content_type)
