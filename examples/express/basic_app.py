from shiny import render, ui
from shiny.express import input

ui.input_slider("n", "N", 1, 100, 50)


@render.text()
def txt():
    return f"n = {input.n()}"
