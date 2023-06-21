from __future__ import annotations

import random

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, reactive, ui


def make_panel(letter: str) -> x.ui.AccordionPanel:
    return x.ui.accordion_panel(
        f"Section {letter}", f"Some narrative for section {letter}"
    )


items = [make_panel(letter) for letter in "ABCDE"]

choices = ["A", "B", "C", "D", "E"]
random.shuffle(choices)

app_ui = ui.page_fluid(
    ui.input_action_button(
        "remove_panel",
        f"Remove Section {choices[-1]}",
        class_="mt-3 mb-3",
    ),
    x.ui.accordion(*items, id="acc", multiple=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    # Copy the list for user
    user_choices = [choice for choice in choices]

    @reactive.Effect
    @reactive.event(input.remove_panel)
    def _():
        if len(user_choices) == 0:
            ui.notification_show("No more panels to remove!")
            return

        # Remove panel
        x.ui.accordion_panel_remove("acc", f"Section { user_choices.pop() }")

        label = "No more panels to remove!"
        if len(user_choices) > 0:
            label = f"Remove Section {user_choices[-1]}"
        ui.update_action_button("remove_panel", label=label)


app = App(app_ui, server)
