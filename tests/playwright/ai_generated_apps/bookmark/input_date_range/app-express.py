from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url")

with ui.card():
    ui.card_header("Bookmarking Date Range Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic date range with default values
    ui.input_date_range(
        id="basic", label="Basic date range", start="2023-01-01", end="2023-12-31"
    )

    @render.text
    def basic_text():
        return f"Date range values: {input.basic()}"

    # module section

    @module
    def date_module(input, output, session):
        ui.h3("Date Range Module")

        # Module date range
        ui.input_date_range(
            id="module_date_range",
            label="Module date range",
            start="2023-06-01",
            end="2023-06-30",
        )

        @render.text
        def date_text():
            return f"Date range values: {input.module_date_range()}"

    date_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
