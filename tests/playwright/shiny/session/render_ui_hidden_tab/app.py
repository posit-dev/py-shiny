import asyncio

from shiny import App, Inputs, Outputs, Session, module, reactive, render, req, ui


@module.ui
def collection_selector_ui():
    return ui.output_ui("collection_selector")


@module.server
def collection_selector_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    selected_collection: reactive.Value,
    collections: reactive.Value,
):
    @render.ui
    def collection_selector():
        req(collections.get())
        return ui.input_select(
            id="internal_selected_collection",
            label="Select Collection",
            choices=collections.get(),
            selected=selected_collection.get(),
        )

    @reactive.effect
    def update_selection():
        selected_collection.set(input.internal_selected_collection())


app_ui = ui.page_fluid(
    ui.navset_tab(
        ui.nav_panel(
            "Tab A",
            ui.card(collection_selector_ui("a"), ui.output_text("a_selected")),
        ),
        ui.nav_panel(
            "Tab B",
            ui.card(collection_selector_ui("b"), ui.output_text("b_selected")),
        ),
        id="tabs",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    a_collection: reactive.Value[str | None] = reactive.Value(None)
    b_collection: reactive.Value[str | None] = reactive.Value(None)
    collections: reactive.Value[dict[str, str] | None] = reactive.Value(None)

    @reactive.effect
    async def load_collections():
        await asyncio.sleep(1.5)
        collections.set({"col_1": "Alpha", "col_2": "Beta", "col_3": "Gamma"})
        a_collection.set("col_1")
        b_collection.set("col_1")

    collection_selector_server(
        "a", selected_collection=a_collection, collections=collections
    )
    collection_selector_server(
        "b", selected_collection=b_collection, collections=collections
    )

    @render.text
    def a_selected():
        val = a_collection.get()
        return f"Selected: {val}" if val else "Loading..."

    @render.text
    def b_selected():
        val = b_collection.get()
        return f"Selected: {val}" if val else "Loading..."


app = App(app_ui, server)
