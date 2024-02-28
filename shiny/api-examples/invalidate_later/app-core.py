import random

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(ui.output_text("value"))


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def value():
        reactive.invalidate_later(0.5)
        return "Random int: " + str(random.randint(0, 10000))


app = App(app_ui, server)
