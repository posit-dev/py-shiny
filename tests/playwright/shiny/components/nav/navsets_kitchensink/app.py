from typing import Any, Dict

from shiny import ui as core_ui
from shiny.express import expressify, ui

ui.page_opts(title="Navsets kitchensink App", id="navsets_collection")


def navset_sidebar():
    return core_ui.sidebar(core_ui.markdown("Sidebar content"))


navset_configs: Dict[str, Dict[str, Dict[str, Any]]] = {
    "navset_pill": {
        "default": {},
        "with_header_footer": {
            "header": {
                "content": "navset_pill_with_header_footer header",
                "id": "navset_pill_header",
            },
            "footer": {
                "content": "navset_pill_with_header_footer footer",
                "id": "navset_pill_footer",
            },
        },
        "selected": {"selected": "navset_pill_b"},
    },
    "navset_underline": {
        "default": {},
        "with_header_footer": {
            "header": {
                "content": "navset_underline_with_header_footer header",
                "id": "navset_underline_header",
            },
            "footer": {
                "content": "navset_underline_with_header_footer footer",
                "id": "navset_underline_footer",
            },
        },
        "selected": {"selected": "navset_underline_b"},
    },
    "navset_tab": {
        "default": {},
        "with_header_footer": {
            "header": {
                "content": "navset_tab_with_header_footer header",
                "id": "navset_tab_header",
            },
            "footer": {
                "content": "navset_tab_with_header_footer footer",
                "id": "navset_tab_footer",
            },
        },
        "selected": {"selected": "navset_tab_b"},
    },
    "navset_pill_list": {
        "default": {},
        "with_header_footer": {
            "header": {
                "content": "navset_pill_list_with_header_footer header",
                "id": "navset_pill_list_header",
            },
            "footer": {
                "content": "navset_pill_list_with_header_footer footer",
                "id": "navset_pill_list_footer",
            },
        },
        "selected": {"selected": "navset_pill_list_b"},
        "widths_no_well": {"widths": (10, 2), "well": False},
    },
    "navset_card_pill": {
        "with_header_footer": {
            "title": "navset_card_pill_with_header_footer",
            "header": {
                "content": "navset_card_pill_with_header_footer header",
                "id": "navset_card_pill_header",
            },
            "footer": {
                "content": "navset_card_pill_with_header_footer footer",
                "id": "navset_card_pill_footer",
            },
        },
        "default": {},
        "placement": {"placement": "below"},
        "selected": {"selected": "navset_card_pill_b"},
        "with_sidebar": {"sidebar": navset_sidebar()},
    },
    "navset_card_tab": {
        "with_header_footer": {
            "title": "navset_card_tab_with_header_footer",
            "header": {
                "content": "navset_card_tab_with_header_footer header",
                "id": "navset_card_tab_header",
            },
            "footer": {
                "content": "navset_card_tab_with_header_footer footer",
                "id": "navset_card_tab_footer",
            },
        },
        "default": {},
        "selected": {"selected": "navset_card_tab_b"},
        "with_sidebar": {"sidebar": navset_sidebar()},
    },
    "navset_card_underline": {
        "with_header_footer": {
            "title": "navset_card_underline_with_header_footer",
            "header": {
                "content": "navset_card_underline_with_header_footer header",
                "id": "navset_card_underline_header",
            },
            "footer": {
                "content": "navset_card_underline_with_header_footer footer",
                "id": "navset_card_underline_footer",
            },
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
        navset_kwargs = params.copy()

        if "header" in navset_kwargs:
            header_content = navset_kwargs["header"]["content"]
            header_id = navset_kwargs["header"]["id"]
            navset_kwargs["header"] = ui.tags.div(header_content, id=f"{header_id}")

        if "footer" in navset_kwargs:
            footer_content = navset_kwargs["footer"]["content"]
            footer_id = navset_kwargs["footer"]["id"]
            navset_kwargs["footer"] = ui.tags.div(footer_content, id=f"{footer_id}")

        with navset_function(id=f"{navset_type}_{navset_id}", **navset_kwargs):
            for suffix in ["a", "b", "c"]:
                with ui.nav_panel(f"{navset_type}_{suffix}"):
                    ui.markdown(f"{navset_type}_{suffix} content")


with ui.navset_tab(id="navsets_collection"):
    for navset_type in navset_configs.keys():
        with ui.nav_panel(navset_type):
            create_navset(navset_type)
