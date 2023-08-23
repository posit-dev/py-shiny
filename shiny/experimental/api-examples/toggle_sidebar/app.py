from __future__ import annotations

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = x.ui.page_sidebar(
    x.ui.sidebar("Sidebar content", id="sidebar"),
    ui.input_action_button(
        "toggle_sidebar",
        label="Toggle sidebar",
        width="fit-content",
    ),
    ui.output_text_verbatim("state"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.toggle_sidebar)
    def _():
        x.ui.toggle_sidebar("sidebar")

    @output
    @render.text
    def state():
        return f"input.sidebar(): {input.sidebar()}"


app = App(app_ui, server=server)
