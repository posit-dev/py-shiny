from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url")

with ui.card():
    ui.card_header("Bookmarking Text Area Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic text area with value
    ui.input_text_area(id="basic", label="Basic text area", value="Enter text here")

    @render.text
    def basic_text():
        return f"Text area value: {input.basic()}"

    # module section

    @module
    def text_area_module(input, output, session):
        ui.h3("Text Area Module")

        # Module text area with value
        ui.input_text_area(
            id="module_text_area",
            label="Module text area",
            value="Enter module text here",
        )

        @render.text
        def text_area_text():
            return f"Text area value: {input.module_text_area()}"

    text_area_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
