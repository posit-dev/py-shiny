from shiny import render, ui
from shiny.express import input, layout

with layout.accordion(id="express_accordion", open=["Panel 1", "Panel 2"]):
    with layout.accordion_panel("Panel 1"):
        ui.input_slider("n", "N", 1, 100, 50)

    with layout.accordion_panel("Panel 2"):

        @render.text
        def txt():
            return f"n = {input.n()}"
