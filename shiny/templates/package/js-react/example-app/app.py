# pyright: basic

from custom_component import (
    input_custom_component,
    output_custom_component,
    render_custom_component,
)

from shiny import App, ui

app_ui = ui.page_fluid(
    ui.h2("Color picker"),
    input_custom_component("color"),
    ui.br(),
    ui.h2("Output color"),
    output_custom_component("value"),
)


def server(input, output, session):
    @render_custom_component
    def value():
        print("Calculating value")
        return input.color()


app = App(app_ui, server, debug=True)
