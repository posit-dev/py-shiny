from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url")

with ui.card():
    ui.card_header("Bookmarking Radio Buttons Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic radio buttons with choices
    ui.input_radio_buttons(
        id="basic",
        label="Basic radio buttons",
        choices=["Option 1", "Option 2", "Option 3"],
    )

    @render.text
    def basic_text():
        return f"Radio button value: {input.basic()}"

    # module section

    @module
    def radio_module(input, output, session):
        ui.h3("Radio Buttons Module")

        # Module radio buttons with choices
        ui.input_radio_buttons(
            id="module_radio",
            label="Module radio buttons",
            choices=["Choice A", "Choice B", "Choice C"],
        )

        @render.text
        def radio_text():
            return f"Radio button value: {input.module_radio()}"

    radio_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
