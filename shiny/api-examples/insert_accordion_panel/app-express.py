import random

from shiny import reactive
from shiny.express import expressify, input, ui

with ui.sidebar():
    ui.input_action_button("add_panel", "Add random panel", class_="mt-3 mb-3"),

with ui.accordion(id="acc", multiple=True):
    for letter in "ABCDE":
        with ui.accordion_panel(f"Section {letter}"):
            f"Some narrative for section {letter} "
            "more narrative"


@reactive.effect
@reactive.event(input.add_panel)
@expressify
def _():
    letter = str(random.randint(0, 10000))
    with ui.hold() as panel:
        with ui.accordion_panel(f"Section {letter}"):
            f"Some narrative for section {letter} "
            "more narrative"

    ui.insert_accordion_panel("acc", panel[0])
