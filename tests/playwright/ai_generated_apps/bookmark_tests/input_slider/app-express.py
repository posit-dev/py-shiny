from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url")

with ui.card():
    ui.card_header("Bookmarking Slider Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic slider
    ui.input_slider(id="basic", label="Basic slider", min=0, max=100, value=50)

    @render.text
    def basic_text():
        return f"Slider value: {input.basic()}"

    # module section

    @module
    def slider_module(input, output, session):
        ui.h3("Slider Module")

        # Module slider
        ui.input_slider(
            id="module_slider", label="Module slider", min=0, max=100, value=50
        )

        @render.text
        def slider_text():
            return f"Slider value: {input.module_slider()}"

    slider_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
