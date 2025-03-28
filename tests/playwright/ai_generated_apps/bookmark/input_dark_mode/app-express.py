from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url")

with ui.card():
    ui.card_header("Bookmarking Dark Mode Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic dark mode toggle
    ui.input_dark_mode(id="basic", label="Basic dark mode toggle", mode="dark")

    @render.text
    def basic_text():
        return f"Dark mode value: {input.basic()}"

    # module section

    @module
    def dark_mode_module(input, output, session):
        ui.h3("Dark Mode Module")

        # Module dark mode toggle
        ui.input_dark_mode(
            id="module_dark_mode", label="Module dark mode toggle", mode="dark"
        )

        @render.text
        def dark_mode_text():
            return f"Dark mode value: {input.module_dark_mode()}"

    dark_mode_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
