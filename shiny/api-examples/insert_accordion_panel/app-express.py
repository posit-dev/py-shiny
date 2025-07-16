import random

from shiny import reactive, ui
from shiny.express import input


def make_panel(letter):
    return ui.accordion_panel(
        f"Section {letter}", f"Some narrative for section {letter}"
    )


ui.input_action_button("add_panel", "Add random panel", class_="mt-3 mb-3")
ui.accordion(*[make_panel(letter) for letter in "ABCDE"], id="acc", multiple=True)


@reactive.effect
@reactive.event(input.add_panel)
def _():
    ui.insert_accordion_panel("acc", make_panel(str(random.randint(0, 10000))))
