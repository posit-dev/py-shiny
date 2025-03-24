from typing import Any, Dict

from shiny.express import expressify, module, session, ui

ui.page_opts(
    title="Navsets kitchensink App", id="navsets_collection", bookmark_store="url"
)


navset_configs: Dict[str, Dict[str, Dict[str, Any]]] = {
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


with ui.card():
    ui.card_header("Bookmarking Navset Demo")

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
