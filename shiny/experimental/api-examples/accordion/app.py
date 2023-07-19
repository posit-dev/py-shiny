from __future__ import annotations

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, reactive, ui

items = [
    x.ui.accordion_panel(f"Section {letter}", f"Some narrative for section {letter}")
    for letter in "ABCDE"
]

# # First shown by default
# x.ui.accordion(*items)

# # Nothing shown by default
# x.ui.accordion(*items, open=False)
# # Everything shown by default
# x.ui.accordion(*items, open=True)

# # Show particular sections
# x.ui.accordion(*items, open="Section B")
# x.ui.accordion(*items, open=["Section A", "Section B"])

app_ui = ui.page_fluid(
    # Provide an id to create a shiny input binding
    x.ui.accordion(*items, id="acc"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        print(input.acc())


app = App(app_ui, server)
