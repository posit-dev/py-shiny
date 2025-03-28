from typing import Any, Dict

from shiny import Inputs, reactive
from shiny.express import app_opts, expressify, input, module, session, ui

app_opts(bookmark_store="url")


navset_configs: Dict[str, Dict[str, Dict[str, Any]]] = {
    "navset_hidden": {
        "default": {},
    },
}


@expressify
def create_navset(navset_name: str, input: Inputs) -> None:
    navset_function = getattr(ui, navset_name)

    @expressify
    def make_navset(navset_variant: str, **navset_kwargs):
        letters = ["a", "b", "c"]
        navset_fn_id = f"{navset_name}_{navset_variant}"
        ui.h3(f"Variant: {navset_variant}")
        with navset_function(id=navset_fn_id, **navset_kwargs):
            for suffix in letters:
                id = f"{navset_fn_id}_{suffix}"
                with ui.nav_panel(id, value=id):
                    ui.markdown(f"{id} content")

        btn_id = f"{navset_fn_id}_button"
        ui.input_action_button(
            id=btn_id,
            label=f"Cycle content for {navset_fn_id}",
        )

        @reactive.effect
        @reactive.event(input[btn_id], ignore_init=True)
        def _():
            # Cycle the content by changing the nav panel value
            current_idx = input[btn_id]()
            next_letter = letters[current_idx % len(letters)]
            next_id = f"{navset_fn_id}_{next_letter}"

            ui.update_navs(navset_fn_id, selected=next_id)

    for navset_variant, params in navset_configs[navset_name].items():
        make_navset(navset_variant, **params.copy())


with ui.card():
    ui.card_header("Hidden Bookmark Navset Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    with ui.navset_tab(id="navsets_collection"):
        for navset_name in navset_configs.keys():
            with ui.nav_panel(navset_name):
                create_navset(navset_name, input=input)

    @module
    def navset_module(input, output, session):
        ui.h3("Navset Module")

        with ui.navset_tab(id="navsets_collection"):
            for navset_name in navset_configs.keys():
                with ui.nav_panel(navset_name):
                    create_navset(navset_name, input=input)

    navset_module("first")

    ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
