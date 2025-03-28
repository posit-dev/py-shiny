from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url", debug=True)

with ui.card():
    ui.card_header("Bookmarking Checkbox Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic checkbox with default value (False)
    ui.input_checkbox(id="basic", label="Basic checkbox")

    @render.text
    def basic_text():
        return f"Checkbox value: {input.basic()}"

    # module section

    @module
    def checkbox_module(input, output, session):
        ui.h3("Checkbox Module")

        # Basic checkbox with default value (True)
        ui.input_checkbox(id="module_checkbox", label="Basic module checkbox")

        @render.text
        def checkbox_text():
            return f"Checkbox value: {input.module_checkbox()}"

    checkbox_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
