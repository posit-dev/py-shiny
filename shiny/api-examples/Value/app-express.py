from shiny import reactive
from shiny.express import input, render, ui

val = reactive.value(0)


@reactive.effect
@reactive.event(input.minus)
def _():
    newVal = val.get() - 1
    val.set(newVal)


@reactive.effect
@reactive.event(input.plus)
def _():
    newVal = val.get() + 1
    val.set(newVal)


with ui.sidebar():
    ui.input_action_button("minus", "-1")
    ui.input_action_button("plus", "+1")


@render.text
def value():
    return str(val.get())
