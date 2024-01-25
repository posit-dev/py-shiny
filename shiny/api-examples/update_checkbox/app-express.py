from shiny import reactive
from shiny.express import input, ui

"Checkbox will be checked when slider is an odd number."
ui.input_slider("controller", "Controller", min=0, max=10, value=0, step=1)
ui.input_checkbox("inCheckbox", "Input checkbox")


@reactive.Effect
def _():
    # True if controller is odd, False if even.
    x_even = input.controller() % 2 == 1
    ui.update_checkbox("inCheckbox", value=x_even)
