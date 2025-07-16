from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("btn_show", "Show popover", class_="mt-3 me-3")
ui.input_action_button("btn_close", "Close popover", class_="mt-3 me-3")

ui.br()
ui.br()

with ui.popover(id="popover_id"):
    ui.input_action_button("btn_w_popover", "A button w/ a popover", class_="mt-3")
    "A message"


@reactive.effect
@reactive.event(input.btn_show)
def _():
    ui.update_popover("popover_id", show=True)


@reactive.effect
@reactive.event(input.btn_close)
def _():
    ui.update_popover("popover_id", show=False)


@reactive.effect
@reactive.event(input.btn_w_popover)
def _():
    ui.notification_show("Button clicked!", duration=3, type="message")
