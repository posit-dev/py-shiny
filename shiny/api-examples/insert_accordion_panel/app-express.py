import random

from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("add_panel", "Add random panel", class_="mt-3 mb-3")

with ui.accordion(id="acc", multiple=True):
    for letter in "ABCDE":
        with ui.accordion_panel(f"Section {letter}"):
            f"Some narrative for section {letter}"


@reactive.effect
@reactive.event(input.add_panel)
def _():
    ui.insert_accordion_panel(
        "acc",
        f"Section {random.randint(0, 10000)}",
        f"Some narrative for section {random.randint(0, 10000)}",
    )
