import shiny.ui
from shiny.express import input, render, ui

# `ui.hold() as x` can be used to save `x` for later output
with ui.hold() as hello_card:
    with ui.card():
        with ui.span():
            "This is a"
            ui.span(" card", style="color: red;")

hello_card

hello_card

ui.hr()


# `ui.hold()` can be used to just suppress output
with ui.hold():

    @render.code()
    def txt():
        return f"Slider value: {input.n()}"


ui.input_slider("n", "N", 1, 100, 50)

shiny.ui.output_code("txt")
