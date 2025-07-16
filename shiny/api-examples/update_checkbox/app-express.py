from shiny import reactive
from shiny.express import input, ui

ui.input_slider("controller", "Controller", min=0, max=1, value=0, step=1)
ui.input_checkbox("inCheckbox", "Input checkbox")


@reactive.effect
def _():
    # True if controller is odd, False if even.
    x_even = input.controller() % 2 == 1
    ui.update_checkbox("inCheckbox", value=x_even)
