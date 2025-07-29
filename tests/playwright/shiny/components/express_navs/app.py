from shiny import Inputs, Outputs, Session, reactive
from shiny.express import module, ui


@module
def my_nav(input: Inputs, output: Outputs, session: Session):
    with ui.navset_card_tab(id="navset"):
        with ui.nav_panel("Panel 1"):
            "This is the first panel"
            ui.input_action_button("hide_tab", "Hide panel 2")
            ui.input_action_button("show_tab", "Show panel 2")
            ui.input_action_button("delete_tabs", "Delete panel 2")

    @reactive.effect
    def _():
        ui.insert_nav_panel(
            "navset",
            "Panel 2",
            "This is the second panel",
        )

    @reactive.effect
    @reactive.event(input.show_tab)
    def _():
        ui.update_nav_panel("navset", target="Panel 2", method="show")

    @reactive.effect
    @reactive.event(input.hide_tab)
    def _():
        ui.update_nav_panel("navset", target="Panel 2", method="hide")

    @reactive.effect
    @reactive.event(input.delete_tabs)
    def _():
        ui.remove_nav_panel("navset", "Panel 2")


my_nav("foo")
my_nav("bar")
