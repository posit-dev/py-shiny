from shiny import reactive, req
from shiny.express import input, ui

ui.input_action_button("btn_show", "Show popover", class_="mt-3 me-3")
ui.input_action_button("btn_close", "Close popover", class_="mt-3 me-3")

ui.br()
ui.br()

with ui.popover(id="popover_id"):
    ui.input_action_button("btn_w_popover", "A button w/ a popover", class_="mt-3")
    "A message"


@reactive.effect
def _():
    req(input.btn_show())

    ui.update_popover("popover_id", show=True)


@reactive.effect
def _():
    req(input.btn_close())

    ui.update_popover("popover_id", show=False)


@reactive.effect
def _():
    req(input.btn_w_popover())
    ui.notification_show("Button clicked!", duration=3, type="message")
