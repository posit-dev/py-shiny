from shiny.express import input, render, ui

ui.input_switch("somevalue", "Some value", False)


@render.text
def value():
    return input.somevalue()
