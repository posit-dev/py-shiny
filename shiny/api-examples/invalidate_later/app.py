import random

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(ui.output_ui("value"))


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        reactive.invalidate_later(0.5)
        print("Random int: ", random.randint(0, 10000))

    @output
    @render.ui
    def value():
        reactive.invalidate_later(0.5)
        return "Random int: " + str(random.randint(0, 10000))


app = App(app_ui, server)
