from shiny import reactive
from shiny.express import input, render, ui

ui.input_text("text", "Type quickly")


# Update at most once per second
@reactive.calc
@reactive.throttle(1)
def text_throttled():
    return input.text()


@render.text
def raw():
    return f"Raw: {input.text()}"


@render.text
def throttled():
    return f"Throttled: {text_throttled()}"
