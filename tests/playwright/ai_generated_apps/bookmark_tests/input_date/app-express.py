from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url")

with ui.card():
    ui.card_header("Bookmarking Date Input Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic date input
    ui.input_date(
        id="basic",
        label="Basic date input",
        value="2024-01-01",
    )

    @render.text
    def basic_text():
        return f"Date value: {input.basic()}"

    # module section

    @module
    def date_module(input, output, session):
        ui.h3("Date Input Module")

        # Module date input
        ui.input_date(
            id="module_date",
            label="Module date input",
            value="2024-01-01",
        )

        @render.text
        def date_text():
            return f"Date value: {input.module_date()}"

    date_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
