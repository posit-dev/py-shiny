from shiny.express import input, render, ui

ui.input_numeric("obs", "Observations:", 10, min=1, max=100)


@render.code
def value():
    return input.obs()
