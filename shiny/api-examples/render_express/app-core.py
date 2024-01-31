import datetime

from shiny.express import input, render, ui

with ui.card(id="card"):
    ui.input_slider("val", "slider", 0, 100, 50)
    "Text outside of render express call"
    ui.tags.br()
    f"Rendered time: {str(datetime.datetime.now())}"

    @render.express
    def render_express():
        "Text inside of render express call"
        ui.tags.br()
        "Dynamic slider value: "
        input.val()
        ui.tags.br()
        f"Rendered time: {str(datetime.datetime.now())}"
