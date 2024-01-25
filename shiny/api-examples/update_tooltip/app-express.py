from shiny import reactive, req
from shiny.express import input, ui

with ui.sidebar():
    ui.input_action_button("btn_show", "Show tooltip", class_="mt-3 me-3")
    ui.input_action_button("btn_close", "Close tooltip", class_="mt-3 me-3")
    ui.input_action_button(
        "btn_update", "Update tooltip phrase (and show tooltip)", class_="mt-3 me-3"
    )
    with ui.tooltip(id="tooltip_id"):
        ui.input_action_button("btn_w_tooltip", "A button w/ a tooltip", class_="mt-3")
        "A message"


@reactive.Effect
def _():
    req(input.btn_show())

    ui.update_tooltip("tooltip_id", show=True)


@reactive.Effect
def _():
    req(input.btn_close())

    ui.update_tooltip("tooltip_id", show=False)


@reactive.Effect
@reactive.event(input.btn_update)
def _():
    content = "A " + " ".join(["NEW" for _ in range(input.btn_update())]) + " message"

    ui.update_tooltip("tooltip_id", content, show=True)


@reactive.Effect
def _():
    req(input.btn_w_tooltip())
    ui.notification_show("Button clicked!", duration=3, type="message")
