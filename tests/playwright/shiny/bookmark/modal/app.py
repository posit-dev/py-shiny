from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, reactive, ui


def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"]),
    )


def server(input: Inputs, output: Outputs, session: Session):

    @reactive.effect
    @reactive.event(input.letter, ignore_init=True)
    async def _():
        await session.bookmark()

    # Just to make sure that missing inputs don't break bookmarking
    # behavior (https://github.com/posit-dev/py-shiny/pull/2117)
    @reactive.effect
    @reactive.event(input.non_existent_input)
    def _():
        pass


app = App(app_ui, server, bookmark_store="url")
