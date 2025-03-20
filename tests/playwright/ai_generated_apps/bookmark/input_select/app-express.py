from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url")

with ui.card():
    ui.card_header("Bookmarking Select Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic select with choices
    ui.input_select(
        id="basic",
        label="Basic select",
        choices={"option1": "Option 1", "option2": "Option 2", "option3": "Option 3"},
    )

    @render.text
    def basic_text():
        return f"Select value: {input.basic()}"

    # module section

    @module
    def select_module(input, output, session):
        ui.h3("Select Module")

        # Module select with choices
        ui.input_select(
            id="module_select",
            label="Module select",
            choices={
                "choiceA": "Choice A",
                "choiceB": "Choice B",
                "choiceC": "Choice C",
            },
        )

        @render.text
        def select_text():
            return f"Select value: {input.module_select()}"

    select_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
