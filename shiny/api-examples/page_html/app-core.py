from pathlib import Path

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_html(Path(__file__).parent / "index.html")


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def greeting():
        return "Hello from the server!"


app = App(app_ui, server)
