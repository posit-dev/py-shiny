"""
Test app for bookmark callbacks (on_restore and on_restored).

This app tracks when callbacks are invoked to verify they execute
in the correct order during bookmark restoration.
"""

from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.bookmark import RestoreState
from shiny.bookmark._save_state import BookmarkState


def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_text("text_input", "Enter text:", value="initial"),
        ui.input_action_button("save_bookmark", "Save Bookmark"),
        ui.hr(),
        ui.h4("Callback Log:"),
        ui.output_code("callback_log"),
        ui.h4("Current State:"),
        ui.output_code("restore_state_info"),
    )


def server(input: Inputs, output: Outputs, session: Session):
    # Track callback invocations
    callback_log_data: reactive.Value[list[str]] = reactive.value([])

    @reactive.effect
    @reactive.event(input.save_bookmark)
    async def _():
        await session.bookmark()

    @session.bookmark.on_bookmark
    async def _(state: BookmarkState):
        log = callback_log_data()
        new_log = log + ["on_bookmark"]
        callback_log_data.set(new_log)

    @session.bookmark.on_bookmarked
    async def _(url: str):
        log = callback_log_data()
        new_log = log + ["on_bookmarked"]
        callback_log_data.set(new_log)
        await session.bookmark.update_query_string(url)

    @session.bookmark.on_restore
    def _(state: RestoreState):
        log = callback_log_data()
        new_log = log + [
            f"on_restore: text_input={state.input.get('text_input', 'N/A')}"
        ]
        callback_log_data.set(new_log)

    @session.bookmark.on_restored
    def _(state: RestoreState):
        log = callback_log_data()
        new_log = log + [
            f"on_restored: text_input={state.input.get('text_input', 'N/A')}"
        ]
        callback_log_data.set(new_log)

    @render.code
    def callback_log():
        return "\n".join(callback_log_data())

    @render.code
    def restore_state_info():
        return f"Current text_input value: {input.text_input()}"


app = App(app_ui, server, bookmark_store="url")
