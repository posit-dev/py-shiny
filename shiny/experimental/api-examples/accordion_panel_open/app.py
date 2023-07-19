from __future__ import annotations

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, reactive, ui

items = [
    x.ui.accordion_panel(f"Section {letter}", f"Some narrative for section {letter}")
    for letter in "ABCDE"
]

app_ui = ui.page_fluid(
    ui.input_action_button("open_acc", "Open Section C", class_="mt-3 mb-3"),
    x.ui.accordion(*items, id="acc", multiple=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.open_acc)
    def _():
        x.ui.accordion_panel_open("acc", "Section C")


app = App(app_ui, server)
