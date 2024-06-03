from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("add", "Add UI")


@reactive.effect
@reactive.event(input.add)
def _():
    ui.insert_ui(
        ui.input_text("txt" + str(input.add()), "Enter some text"),
        selector="#add",
        where="afterEnd",
    )
