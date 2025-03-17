from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, reactive, ui


def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"]),
    )


def server(input: Inputs, ouput: Outputs, session: Session):

    @reactive.effect
    @reactive.event(input.letter, ignore_init=True)
    async def _():
        await session.bookmark()


app = App(app_ui, server, bookmark_store="url")
