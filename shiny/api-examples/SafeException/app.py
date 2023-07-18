from shiny import App, Inputs, Outputs, Session, render, ui
from shiny.types import SafeException

app_ui = ui.page_fluid(ui.output_ui("safe"), ui.output_ui("unsafe"))


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.ui
    def safe():
        raise SafeException("This is a safe exception")

    @output
    @render.ui
    def unsafe():
        raise Exception("This is an unsafe exception")


app = App(app_ui, server)
app.sanitize_errors = True
