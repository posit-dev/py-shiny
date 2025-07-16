from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("btn_show", "Show tooltip", class_="mt-3 me-3")
ui.input_action_button("btn_close", "Close tooltip", class_="mt-3 me-3")
ui.input_action_button(
    "btn_update", "Update tooltip phrase (and show tooltip)", class_="mt-3 me-3"
)

with ui.tooltip(id="tooltip_id"):
    ui.input_action_button(
        "btn_w_tooltip",
        "A button w/ a tooltip",
        class_="btn-primary mt-5",
    )
    "A message"


@reactive.effect
@reactive.event(input.btn_show)
def _():
    ui.update_tooltip("tooltip_id", show=True)


@reactive.effect
@reactive.event(input.btn_close)
def _():
    ui.update_tooltip("tooltip_id", show=False)


@reactive.effect
@reactive.event(input.btn_update)
def _():
    content = "A " + " ".join(["NEW" for _ in range(input.btn_update())]) + " message"

    ui.update_tooltip("tooltip_id", content, show=True)


@reactive.effect
@reactive.event(input.btn_w_tooltip)
def _():
    ui.notification_show("Button clicked!", duration=3, type="message")
