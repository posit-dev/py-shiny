"""The app the `local_server` fixture finds by default: `app.py` beside the test."""

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fixed(ui.output_text("doubled"))


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def doubled():
        return str(input.n() * 2)


app = App(app_ui, server)
