import random

from shiny import App, Inputs, reactive, render, ui

app_ui = ui.page_fluid(ui.output_text("value"))


def server(input: Inputs):
    @render.text
    def value():
        reactive.invalidate_later(0.5)
        return "Random int: " + str(random.randint(0, 10000))


app = App(app_ui, server)
