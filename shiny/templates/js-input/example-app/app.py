# pyright: basic

from shiny import ui, App, render

from customInputComponent import custom_input


app_ui = ui.page_fluid(
    custom_input("myInput"),
    ui.output_text("valueOut"),
)


def server(input, output, session):
    @render.text
    def valueOut():
        return f"Value from input is {input.myInput()}"


app = App(app_ui, server)
