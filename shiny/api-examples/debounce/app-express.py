from shiny import reactive
from shiny.express import input, render, ui

ui.input_text("text", "Type quickly")


# Update only after typing stops for 1 second
@reactive.calc
@reactive.debounce(1)
def text_debounced():
    return input.text()


@render.text
def raw():
    return f"Raw: {input.text()}"


@render.text
def debounced():
    return f"Debounced: {text_debounced()}"
