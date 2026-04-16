from faicons import icon_svg

from shiny import reactive
from shiny.express import input, render, ui

ui.h2("Update Toolbar Input Button Examples")
ui.p("These examples demonstrate updating a toolbar button's label and icon on click.")

with ui.card():
    with ui.card_header():
        "Update Label"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button("btn", label="Click me")

    with ui.card_body():

        @render.text
        def count():
            return f"Button clicked {input.btn()} times"


@reactive.effect
@reactive.event(input.btn)
def _():
    if input.btn() == 1:
        ui.update_toolbar_input_button("btn", label="Clicked!")


with ui.card():
    with ui.card_header():
        "Update Icon"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(
                "btn_icon", label="Save", icon=icon_svg("floppy-disk")
            )

    with ui.card_body():

        @render.text
        def count_icon():
            return f"Button clicked {input.btn_icon()} times"


@reactive.effect
@reactive.event(input.btn_icon)
def _():
    if input.btn_icon() == 1:
        ui.update_toolbar_input_button(
            "btn_icon", icon=icon_svg("circle-check"), label="Saved"
        )
