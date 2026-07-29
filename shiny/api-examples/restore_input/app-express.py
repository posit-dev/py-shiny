from htmltools import css, tags

from shiny.bookmark import restore_input
from shiny.express import app_opts, session, ui
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


# `bookmark_store` (`"url"` or `"server"`) must be set to enable bookmarking.
app_opts(bookmark_store="url")

custom_input_text(
    "myid",
    value="Change this value, then click bookmark and refresh the page.",
)
ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
