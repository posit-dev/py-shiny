import random

from shiny import reactive
from shiny.express import input, ui

choices = ["A", "B", "C", "D", "E"]
random.shuffle(choices)

ui.input_action_button(
    "remove_panel",
    f"Remove Section {choices[-1]}",
    class_="mt-3 mb-3",
)

" (Sections randomly picked at server start)"

with ui.accordion(id="acc", multiple=True):
    for letter in "ABCDE":
        with ui.accordion_panel(f"Section {letter}"):
            f"Some narrative for section {letter}"


@reactive.effect
@reactive.event(input.remove_panel)
def _():
    if len(choices) == 0:
        ui.notification_show("No more panels to remove!")
        return

    ui.remove_accordion_panel("acc", f"Section {choices.pop()}")

    label = "No more panels to remove!"
    if len(choices) > 0:
        label = f"Remove Section {choices[-1]}"
    ui.update_action_button("remove_panel", label=label)
