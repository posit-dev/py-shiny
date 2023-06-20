from shiny import App, Inputs, Outputs, Session, render, ui
from shiny.types import SilentCancelOutputException

app_ui = ui.page_fluid(
    ui.input_text(
        "txt",
        "Delete the input text completely: it won't get removed below the input",
        "Some text",
        width="400px",
    ),
    ui.output_ui("txt_out"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.ui
    def txt_out():
        if not input.txt():
            raise SilentCancelOutputException()
        return "Your input: " + input.txt()


app = App(app_ui, server)
