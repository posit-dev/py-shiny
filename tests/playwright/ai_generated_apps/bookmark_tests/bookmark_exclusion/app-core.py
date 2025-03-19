from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, module, ui
from shiny.bookmark import BookmarkState, RestoreState


@module.ui
def mod_ui(label: str):
    return ui.div(
        ui.input_text("text", f"{label} Text", "Initial Module Text"),
        ui.input_numeric("num", f"{label} Numeric", 1),
        ui.input_text("excluded", f"{label} Excluded", "Module Excluded"),
    )


@module.server
def mod_server(input: Inputs, output: Outputs, session: Session):
    session.bookmark.exclude.append("excluded")

    @session.bookmark.on_bookmark
    async def _(state: BookmarkState):
        state.values["module_num"] = input.num()

    @session.bookmark.on_restore
    def _(state: RestoreState):
        if "module_num" in state.values:
            ui.update_numeric("num", value=state.values["module_num"])
        if "text" in state.input:
            print(f"module on_restore: text: {state.input['text']}")


def app_ui(request: Request):
    return ui.page_fluid(
        mod_ui("mod1", "Module 1"),
        mod_ui("mod2", "Module 2"),
        ui.input_bookmark_button(),
    )


def server(input: Inputs, output: Outputs, session: Session):
    mod_server("mod1")
    mod_server("mod2")

    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)


app = App(app_ui, server, bookmark_store="url")
