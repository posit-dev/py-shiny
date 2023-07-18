from __future__ import annotations

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, reactive, ui


def make_panel(letter: str) -> x.ui.AccordionPanel:
    return x.ui.accordion_panel(
        f"Section {letter}",
        f"Some narrative for section {letter}",
        value=f"sec_{letter}",
    )


items = [make_panel(letter) for letter in "ABCDE"]

app_ui = ui.page_fluid(
    ui.input_switch("update_panel", "Update Sections"),
    x.ui.accordion(*items, id="acc", multiple=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.update_panel)
    def _():
        txt = " (updated)" if input.update_panel() else ""
        for letter in "ABCDE":
            x.ui.update_accordion_panel(
                "acc",
                f"sec_{letter}",
                f"Some{txt} narrative for section {letter}",
                title=f"Section {letter}{txt}",
            )


app = App(app_ui, server)
