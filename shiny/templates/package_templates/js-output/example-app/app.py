from custom_component import custom_component, render_custom_component

from shiny import App, ui

app_ui = ui.page_fluid(
    ui.input_slider("n", "Choose a value", 1, 20, 5),
    custom_component("myOutput"),
)


def server(input, output, session):
    @render_custom_component
    def myOutput():
        return input.n()


app = App(app_ui, server)
