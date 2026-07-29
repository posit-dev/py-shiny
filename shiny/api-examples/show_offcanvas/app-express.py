from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("show_btn", "Show panel")


@reactive.effect
@reactive.event(input.show_btn)
def _():
    ui.show_offcanvas(
        ui.offcanvas(
            ui.p("This panel was inserted dynamically by the server."),
            title="Server Panel",
            placement="left",
        )
    )
