from shiny import req
from shiny.express import input, render, ui

ui.input_checkbox_group(
    "colors",
    "Choose color(s):",
    {
        "red": ui.span("Red", style="color: #FF0000;"),
        "green": ui.span("Green", style="color: #00AA00;"),
        "blue": ui.span("Blue", style="color: #0000AA;"),
    },
)


@render.ui
def val():
    req(input.colors())
    return "You chose " + ", ".join(input.colors())
