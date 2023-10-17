from shiny import render, ui
from shiny.flat import input

ui.input_slider("n", "N", 1, 100, 50)

ui.div("Hey there, I'm a div!")


@render.text()
def txt():
    return f"n = {input.n()}"
