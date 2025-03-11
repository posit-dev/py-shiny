from htmltools import tags
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
        "Custom input text:",
        tags.input(
            id=resolved_id,
            type="text",
            value=restore_input(resolved_id, value),
            placeholder="Type here...",
        ),
        class_="shiny-input-container",
        style=ui.css(width="400px"),
    )


# App UI **must** be a function to ensure that each user restores their own UI values.
def app_ui(request: Request):
    return ui.page_fluid(
        custom_input_text("myid", value="Default value - Hello, world!"),
        ui.input_bookmark_button(),
        # ui.markdown(
        #     "Directions: "
        #     "\n1. Change the radio button selection below"
        #     "\n2. Save the bookmark."
        #     "\n3. Then, refresh your browser page to see the radio button selection has been restored."
        # ),
        # ui.hr(),
        # ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"]),
        # ui.input_bookmark_button(label="Save bookmark!"),
    )


def server(input: Inputs, output: Outputs, session: Session):

    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)


app = App(app_ui, server, bookmark_store="url")
