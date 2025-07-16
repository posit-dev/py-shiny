from shiny.express import input, render, ui

ui.input_checkbox("somevalue", "Some value", False)


@render.ui
def value():
    return input.somevalue()
