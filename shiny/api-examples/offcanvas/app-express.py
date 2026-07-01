from shiny.express import input, render, ui

panel = ui.offcanvas(
    ui.p("This is the offcanvas body content."),
    title="Offcanvas Panel",
    trigger=ui.input_action_button("open_btn", "Open panel"),
    id="panel",
)

panel


@render.text
def state():
    return f"Panel is {'open' if input.panel() else 'closed'}"
