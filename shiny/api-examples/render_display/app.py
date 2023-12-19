import datetime

from shiny import render, ui
from shiny.express import input, layout

with layout.card(id="card"):
    ui.input_slider("val", "slider", 0, 100, 50)
    "Text outside of render display call"
    ui.tags.br()
    f"Rendered time: {str(datetime.datetime.now())}"

    @render.display
    def render_display():
        "Text inside of render display call"
        ui.tags.br()
        "Dynamic slider value: "
        input.val()
        ui.tags.br()
        f"Display's rendered time: {str(datetime.datetime.now())}"
