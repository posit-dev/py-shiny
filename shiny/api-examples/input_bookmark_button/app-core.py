from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, ui


# App UI **must** be a function to ensure that each user restores their own UI values.
def app_ui(request: Request):
    return ui.page_fluid(
        ui.markdown(
            "Directions: "
            "\n1. Change the radio button selection below"
            "\n2. Save the bookmark."
            "\n3. Then, refresh your browser page to see the radio button selection has been restored."
        ),
        ui.hr(),
        ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"]),
        ui.input_bookmark_button(label="Save bookmark!"),
    )


def server(input: Inputs, output: Outputs, session: Session):

    # @reactive.effect
    # @reactive.event(input.letter, ignore_init=True)
    # async def _():
    #     await session.bookmark()

    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)


app = App(app_ui, server, bookmark_store="url")
