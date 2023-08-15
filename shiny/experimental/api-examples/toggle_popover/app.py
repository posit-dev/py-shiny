from __future__ import annotations

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, reactive, req, ui

app_ui = ui.page_fluid(
    ui.input_action_button("btn_show", "Show popover", class_="mt-3 me-3"),
    ui.input_action_button("btn_close", "Close popover", class_="mt-3 me-3"),
    ui.br(),
    ui.input_action_button("btn_toggle", "Toggle popover", class_="mt-3 me-3"),
    ui.br(),
    ui.br(),
    x.ui.popover(
        ui.input_action_button("btn_w_popover", "A button w/ a popover", class_="mt-3"),
        "A message",
        id="popover_id",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        req(input.btn_show())

        x.ui.toggle_popover("popover_id", show=True)

    @reactive.Effect
    def _():
        req(input.btn_close())

        x.ui.toggle_popover("popover_id", show=False)

    @reactive.Effect
    def _():
        req(input.btn_toggle())

        x.ui.toggle_popover("popover_id")

    @reactive.Effect
    def _():
        req(input.btn_w_popover())
        ui.notification_show("Button clicked!", duration=3, type="message")


app = App(app_ui, server=server)
