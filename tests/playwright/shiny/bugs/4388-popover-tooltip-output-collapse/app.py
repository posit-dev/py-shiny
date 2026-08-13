"""
Regression app for bslib #1326 / shiny #4388.

A dynamically-rendered output (`@render.ui`) inside a title-less popover or
tooltip used to collapse to 0 width, so its `ResizeObserver` never fired and
the output stayed stuck "recalculating" forever. Vendored bslib CSS now
gives `.shiny-html-output` a non-zero minimum width inside `.popover` and
`.tooltip` containers so the observer always sees a size change.
"""

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.popover(
        ui.input_action_button("btn_popover", "Popover trigger", class_="mt-3 me-3"),
        ui.output_ui("popover_out"),
        id="popover_id",
    ),
    ui.tooltip(
        ui.input_action_button("btn_tooltip", "Tooltip trigger", class_="mt-3"),
        ui.output_ui("tooltip_out"),
        id="tooltip_id",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.ui
    def popover_out():
        return ui.div("Dynamic content")

    @render.ui
    def tooltip_out():
        return ui.div("Dynamic content")


app = App(app_ui, server=server)
