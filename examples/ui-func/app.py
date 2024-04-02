from datetime import datetime

from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, reactive, render, ui


def app_ui(request: Request):
    return ui.page_fluid(
        ui.div("This page was rendered at ", datetime.now().isoformat()),
        ui.output_text("now"),
    )


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def now():
        reactive.invalidate_later(0.1)
        return f"The current time is {datetime.now().isoformat()}"


app = App(app_ui, server)
