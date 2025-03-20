from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url")

with ui.card():
    ui.card_header("Bookmarking Checkbox Group Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic checkbox group with choices
    ui.input_checkbox_group(
        id="basic",
        label="Basic checkbox group",
        choices=["Option 1", "Option 2", "Option 3"],
    )

    @render.text
    def basic_text():
        return f"Checkbox group values: {input.basic()}"

    # module section

    @module
    def checkbox_module(input, output, session):
        ui.h3("Checkbox Group Module")

        # Module checkbox group with choices
        ui.input_checkbox_group(
            id="module_checkbox",
            label="Module checkbox group",
            choices=["Choice A", "Choice B", "Choice C"],
        )

        @render.text
        def checkbox_text():
            return f"Checkbox group values: {input.module_checkbox()}"

    checkbox_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
