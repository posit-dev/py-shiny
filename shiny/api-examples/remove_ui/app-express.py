from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("rmv", "Remove UI")
ui.input_text("txt", "Click button above to remove me")


@reactive.effect
@reactive.event(input.rmv)
def _():
    ui.remove_ui(selector="div:has(> #txt)")
