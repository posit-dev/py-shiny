# pyright: basic

from custom_component import custom_component

from shiny import App, render, ui

app_ui = ui.page_fluid(
    custom_component("myComponent"),
    ui.output_text("valueOut"),
)


def server(input, output, session):
    @render.text
    def valueOut():
        return f"Value from input is {input.myComponent()}"


app = App(app_ui, server)
