from shiny.express import input, render, ui
from shiny.types import SilentException

ui.input_text(
    "txt",
    "Enter text to see it displayed below the input",
    width="400px",
)


@render.ui
def txt_out():
    if not input.txt():
        raise SilentException()
    return "Your input: " + input.txt()
