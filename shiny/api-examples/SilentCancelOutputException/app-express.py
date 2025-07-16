from shiny.express import input, render, ui
from shiny.types import SilentCancelOutputException

ui.input_text(
    "txt",
    "Delete the input text completely: it won't get removed below the input",
    "Some text",
    width="400px",
)


@render.ui
def txt_out():
    if not input.txt():
        raise SilentCancelOutputException()
    return "Your input: " + input.txt()
