from shiny import reactive
from shiny.express import input, render, ui

ui.input_action_button("add", "Add more controls")


@render.ui
@reactive.event(input.add)
def moreControls():
    return [
        ui.input_slider("n", "N", min=1, max=1000, value=500),
        ui.input_text("label", "Label"),
    ]
