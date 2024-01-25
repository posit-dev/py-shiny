import random

from shiny import reactive
from shiny.express import expressify, input, ui


@expressify
def make_panel(id: str):
    with ui.accordion_panel(f"Section {id}"):
        f"Some narrative for section {id}"


with ui.sidebar():
    ui.input_action_button("add_panel", "Add random panel", class_="mt-3 mb-3"),

with ui.accordion(multiple=False, id="acc"):
    for letter in "ABCDE":
        make_panel(letter)


@reactive.Effect
@reactive.event(input.add_panel)
def _():
    ui.insert_accordion_panel("acc", make_panel("foo"))
