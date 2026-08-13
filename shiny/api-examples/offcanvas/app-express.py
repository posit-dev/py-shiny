from shiny import reactive
from shiny.express import input, render, ui

panel = ui.offcanvas(
    ui.p("This is the offcanvas body content."),
    title="Offcanvas Panel",
    id="panel",
)

panel
ui.input_action_button("toggle_btn", "Toggle panel")
ui.input_action_button("hide_btn", "Hide panel")


@render.text
def state():
    return f"Panel is {'open' if input.panel() else 'closed'}"


@reactive.effect
@reactive.event(input.toggle_btn)
def _():
    ui.toggle_offcanvas("panel")


@reactive.effect
@reactive.event(input.hide_btn)
def _():
    ui.hide_offcanvas("panel")
