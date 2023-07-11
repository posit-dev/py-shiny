from __future__ import annotations

import random

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, reactive, ui


def make_panel(letter: str) -> x.ui.AccordionPanel:
    return x.ui.accordion_panel(
        f"Section {letter}", f"Some narrative for section {letter}"
    )


items = [make_panel(letter) for letter in "ABCDE"]

app_ui = ui.page_fluid(
    ui.input_action_button("add_panel", "Add random panel", class_="mt-3 mb-3"),
    x.ui.accordion(*items, id="acc", multiple=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.add_panel)
    def _():
        x.ui.accordion_panel_insert("acc", make_panel(str(random.randint(0, 10000))))


app = App(app_ui, server)
