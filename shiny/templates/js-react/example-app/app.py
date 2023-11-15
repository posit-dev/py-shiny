# pyright: basic

from shiny import ui, App, render


from customReactComponent import react_input


app_ui = ui.page_fluid(
    react_input("myInput"),
    ui.output_text("valueOut"),
)


def server(input, output, session):
    @render.text
    def valueOut():
        return f"Value from input is {input.myInput()}"


app = App(app_ui, server)
