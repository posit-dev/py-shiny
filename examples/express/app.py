from shiny import render, ui
from shiny.express import input, layout, output_args, suspend_display

ui.input_slider("n", "N", 1, 100, 50)

ui.div("Hey there, I'm a div!")


@output_args(placeholder=True)
@render.text()
def txt():
    return f"n = {input.n()}"


@render.ui
def heading():
    return ui.h3("A Heading")


with suspend_display():
    ui.div("This div should not be displayed")

ui.div("But this one should")

with layout.div(style="color: red;"):
    "Hello"
