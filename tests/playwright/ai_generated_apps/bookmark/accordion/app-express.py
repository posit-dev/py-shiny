from shiny.express import app_opts, expressify, input, module, render, session, ui

app_opts(bookmark_store="url")


@expressify
def my_accordion(**kwargs):
    with ui.accordion(**kwargs):
        for letter in "ABCDE":
            with ui.accordion_panel(f"Section {letter}"):
                f"Some narrative for section {letter}"


ui.h2("Accordion with bookmarking")

with ui.card():
    ui.h3("Accordion non-module bookmarking")
    my_accordion(multiple=False, id="acc_single")

    @render.text
    def accordion_global():
        return f"input.accordion(): {input.acc_single()}"

    # Module section in sidebar
    @module
    def accordion_module(input, output, session):
        my_accordion(multiple=False, id="acc_mod")

        @render.text
        def accordion_module():
            return f"input.acc_mod(): {input.acc_mod()}"

    ui.h3("Accordion module bookmarking")
    accordion_module("first")

    ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
