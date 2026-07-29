from shiny.express import input, render, ui

ui.input_text_area(
    "source",
    "Enter code to display below:",
    "print('Hello, Shiny!')\nfor i in range(3):\n    print(i)",
    rows=8,
)

with ui.card():

    @render.code
    def code_default():
        return input.source()


with ui.card():

    @render.code(placeholder=False)
    def code_no_placeholder():
        return input.source()
