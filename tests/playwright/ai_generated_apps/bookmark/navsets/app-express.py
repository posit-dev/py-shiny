from typing import Any, Dict

from shiny.express import app_opts, expressify, module, session, ui

app_opts(bookmark_store="url")

navset_configs: Dict[str, Dict[str, Dict[str, Any]]] = {
    "navset_bar": {
        "default": {"title": "navset_bar_default"},
    },
    "navset_pill": {
        "default": {},
    },
    "navset_underline": {
        "default": {},
    },
    "navset_tab": {
        "default": {},
    },
    "navset_pill_list": {
        "default": {},
    },
    "navset_card_pill": {
        "default": {},
    },
    "navset_card_tab": {
        "default": {},
    },
    "navset_card_underline": {
        "default": {},
    },
}


@expressify
def create_navset(navset_type: str) -> None:
    navset_function = getattr(ui, navset_type)

    for navset_id, params in navset_configs[navset_type].items():
        navset_kwargs = params.copy()

        with navset_function(id=f"{navset_type}_{navset_id}", **navset_kwargs):
            for suffix in ["a", "b", "c"]:
                id = f"{navset_type}_{suffix}"
                with ui.nav_panel(id, value=id):
                    ui.markdown(f"{navset_type}_{suffix} content")


with ui.card():
    ui.card_header("Bookmarking Navset Kitchensink")

    # Non-modular section
    ui.h3("Non-Module Section")

    with ui.navset_tab(id="navsets_collection"):
        for navset_type in navset_configs.keys():
            with ui.nav_panel(navset_type):
                create_navset(navset_type)

    @module
    def navset_module(input, output, session):
        ui.h3("Navset Module")

        with ui.navset_tab(id="navsets_collection"):
            for navset_type in navset_configs.keys():
                with ui.nav_panel(navset_type):
                    create_navset(navset_type)

    navset_module("first")

    ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
