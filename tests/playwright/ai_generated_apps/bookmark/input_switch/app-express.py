from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url")

with ui.card():
    ui.card_header("Bookmarking Switch Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic switch with choices
    ui.input_switch(id="basic", label="Basic switch", value=False)

    @render.text
    def basic_text():
        return f"Switch value: {input.basic()}"

    # module section

    @module
    def switch_module(input, output, session):
        ui.h3("Switch Module")

        # Module switch
        ui.input_switch(id="module_switch", label="Module switch", value=False)

        @render.text
        def switch_text():
            return f"Switch value: {input.module_switch()}"

    switch_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
