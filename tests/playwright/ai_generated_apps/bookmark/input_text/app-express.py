from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url")

with ui.card():
    ui.card_header("Bookmarking Text Input Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic text input
    ui.input_text(id="basic", label="Basic text input", value="Type something here")

    @render.text
    def basic_text():
        return f"Text input value: {input.basic()}"

    # module section

    @module
    def text_module(input, output, session):
        ui.h3("Text Input Module")

        # Module text input
        ui.input_text(
            id="module_text", label="Module text input", value="Type something here"
        )

        @render.text
        def text_text():
            return f"Text input value: {input.module_text()}"

    text_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
