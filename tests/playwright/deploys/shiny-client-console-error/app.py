from shiny import reactive, render
from shiny.express import input, ui

ui.input_action_button("same_id", "Action")
ui.input_action_button("same_id", "Action")


@render.text()
@reactive.event(input.same_id)
def counter():
    return f"{input.same_id()}"
