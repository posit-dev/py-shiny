from shiny import App, Inputs, Outputs, Session, render, ui
from shiny.types import SilentException

app_ui = ui.page_fluid(
    ui.input_text(
        "txt",
        "Enter text to see it displayed below the input",
        width="400px",
    ),
    ui.output_ui("txt_out"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.ui
    def txt_out():
        if not input.txt():
            raise SilentException()
        return "Your input: " + input.txt()


app = App(app_ui, server)
