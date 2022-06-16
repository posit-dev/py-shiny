from shiny import *

app_ui = ui.page_fluid(
    ui.input_text("txt", "Enter the text to display below:"),
    ui.row(
        ui.column(6, ui.output_text("text")),
        ui.column(6, ui.output_text_verbatim("verb", placeholder=True)),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    def text():
        return input.txt()

    @output
    @render.text
    def verb():
        return input.txt()


app = App(app_ui, server)
