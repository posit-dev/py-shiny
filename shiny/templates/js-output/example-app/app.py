from shiny import ui, App
from customOutputComponent import render_custom_output, custom_output


app_ui = ui.page_fluid(
    ui.input_slider("n", "Choose a value", 1, 20, 5),
    custom_output("myOutput"),
)


def server(input, output, session):
    @render_custom_output
    def myOutput():
        return input.n()


app = App(app_ui, server)
