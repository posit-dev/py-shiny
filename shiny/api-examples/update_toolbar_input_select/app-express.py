from faicons import icon_svg

from shiny import reactive
from shiny.express import input, render, ui

ui.h2("Update Toolbar Input Select Example")
ui.p(
    "This example demonstrates updating a toolbar select's label, choices, icon, and selected value when a button is clicked."
)

with ui.card():
    with ui.card_header():
        with ui.toolbar(align="right"):
            ui.toolbar_input_select("select", label="Choose", choices=["A", "B", "C"])
            ui.toolbar_input_button("update_btn", label="Update Select")

    with ui.card_body():

        @render.text
        def value():
            return str(input.select())


@reactive.effect
@reactive.event(input.update_btn)
def _():
    ui.update_toolbar_input_select(
        "select",
        label="Pick one",
        choices=["New 1", "New 2", "New 3"],
        selected="New 2",
        icon=icon_svg("filter"),
        show_label=True,
    )
