from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui


@module.ui
def mod_ui():
    return ui.div(
        ui.input_text("text_in", "Initial Module Text"),
        ui.output_text("included_module_text"),
        ui.input_numeric("num_in", "Enter number", 1),
        ui.output_text("included_module_num"),
        ui.input_text("text_excl", "Module Excluded"),
        ui.output_text("excluded_module_text"),
    )


@module.server
def mod_server(input: Inputs, output: Outputs, session: Session):
    # 1. Fix: Correct input ID for exclusion
    session.bookmark.exclude.append("text_excl")  # Changed from "excluded"

    @render.text
    def included_module_text():
        return f"Included text: {input.text_in()}"

    @render.text
    def included_module_num():
        return f"Included num: {input.num_in()}"

    @render.text
    def excluded_module_text():
        return f"Excluded text: {input.text_excl()}"

    # 2. Add: Trigger bookmarking when inputs change
    @reactive.effect
    @reactive.event(input.text_in, input.num_in, ignore_init=True)
    async def _():
        await session.bookmark()


def app_ui(request: Request):
    return ui.page_fluid(
        mod_ui("mod1"),
    )


def server(input: Inputs, output: Outputs, session: Session):
    mod_server("mod1")

    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)


app = App(app_ui, server, bookmark_store="url")
