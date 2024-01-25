from shiny.express import input, render, ui

ui.input_text("caption", "Caption:", "Data summary")


@render.code
def value():
    return input.caption()
