from __future__ import annotations

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, reactive, req, ui

app_ui = ui.page_fluid(
    ui.input_action_button("btn_show", "Show tooltip", class_="mt-3 me-3"),
    ui.input_action_button("btn_close", "Close tooltip", class_="mt-3 me-3"),
    ui.br(),
    ui.input_action_button("btn_toggle", "Toggle tooltip", class_="mt-3 me-3"),
    ui.br(),
    ui.br(),
    x.ui.tooltip(
        ui.input_action_button("btn_w_tooltip", "A button w/ a tooltip", class_="mt-3"),
        "A message",
        id="tooltip_id",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        req(input.btn_show())

        x.ui.tooltip_toggle("tooltip_id", show=True)

    @reactive.Effect
    def _():
        req(input.btn_close())

        x.ui.tooltip_toggle("tooltip_id", show=False)

    @reactive.Effect
    def _():
        req(input.btn_toggle())

        x.ui.tooltip_toggle("tooltip_id")

    @reactive.Effect
    def _():
        req(input.btn_w_tooltip())
        ui.notification_show("Button clicked!", duration=3, type="message")


app = App(app_ui, server=server)
