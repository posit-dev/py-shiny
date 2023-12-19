# pyright: basic

from custom_component import (
    input_custom_component,
    output_custom_component,
    render_custom_component,
)

from shiny import App, ui

app_ui = ui.page_fluid(
    input_custom_component("color"),
    output_custom_component("valueOut"),
)


def server(input, output, session):
    @render_custom_component
    def valueOut():
        return input.color()


app = App(app_ui, server)
