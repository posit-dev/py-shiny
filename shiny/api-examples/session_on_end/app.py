from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.bookmark import BookmarkState


# App UI **must** be a function to ensure that each user restores their own UI values.
def app_ui(request: Request):
    return ui.page_fluid(
        ui.markdown(
            "Directions: "
            "\n1. Change the radio buttons below"
            "\n2. Changing the radio button will cause a server error."
            "\n3. The app will save the state to the URL before disconnecting."
            "\n4. Refresh, your browser. The radio button selection should persist."
        ),
        ui.hr(),
        ui.input_radio_buttons(
            "letter",
            "Pick a letter",
            choices=["A", "B", "C"],
        ),
        "Selection:",
        ui.output_code("letter_out"),
    )


def server(input: Inputs, output: Outputs, session: Session):

    @render.code
    def letter_out():
        return input.letter()

    @reactive.effect
    @reactive.event(input.letter, ignore_init=True)
    async def _():
        # Simulate a server error when the radio button is changed
        raise RuntimeError("Simulated server error")

    # When the session ends, update the query string with the latest bookmark information
    @session.on_end
    async def _():
        await session.bookmark.update_query_string()

    # Reset query string when restoring state
    @session.bookmark.on_restored
    async def _(state: BookmarkState):
        await session.bookmark.update_query_string(session.clientdata.url_pathname())


# Make sure to set the bookmark_store to `"url"` (or `"server"`)
# to store the bookmark information/key in the URL query string.
app = App(app_ui, server, bookmark_store="url")
