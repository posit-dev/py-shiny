from shiny import render
from shiny.express import input, ui

ui.input_slider("n", "N", 1, 100, 50)


@render.code()
def txt():
    return f"n = {input.n()}"
