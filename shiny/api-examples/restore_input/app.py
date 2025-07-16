from htmltools import css, tags
from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, ui
from shiny.bookmark import restore_input
from shiny.module import resolve_id


def custom_input_text(
    id: str,
    value: str = "",
) -> ui.Tag:

    resolved_id = resolve_id(id)
    return tags.div(
        tags.label(tags.strong("Custom input text:")),
        tags.textarea(
            restore_input(resolved_id, value),
            id=resolved_id,
            type="text",
            placeholder="Type here...",
            style=css(width="400px", height="3hr"),
        ),
        class_="shiny-input-container",
    )


# App UI **must** be a function to ensure that each user restores their own UI values.
def app_ui(request: Request):
    return ui.page_fluid(
        custom_input_text(
            "myid",
            value="Change this value, then click bookmark and refresh the page.",
        ),
        ui.input_bookmark_button(),
    )


def server(input: Inputs, output: Outputs, session: Session):

    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)


# `bookmark_store` (`"url"` or `"server"`) must be passed to the `App` constructor to enable bookmarking.
app = App(app_ui, server, bookmark_store="url")
