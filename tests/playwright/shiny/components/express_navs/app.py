from shiny import reactive
from shiny.express import ui, module


@module
def my_nav(input, output, session):
    with ui.navset_card_tab(id="navset"):
        with ui.nav_panel("Panel 1"):
            "This is the first panel"
            ui.input_action_button("hideTab", "Hide panel 2")
            ui.input_action_button("showTab", "Show panel 2")
            ui.input_action_button("deleteTabs", "Delete panel 2")

    @reactive.effect
    def _():
        ui.insert_nav_panel(
            "navset",
            "Panel 2",
            "This is the second panel",
        )

        @reactive.effect()
        @reactive.event(input.showTab)
        def _():
            ui.show_nav_panel("navset", target="Panel 2")

        @reactive.effect()
        @reactive.event(input.hideTab)
        def _():
            ui.hide_nav_panel("navset", target="Panel 2")

        @reactive.effect()
        @reactive.event(input.deleteTabs)
        def _():
            ui.remove_nav_panel("navset", "Panel 2")


my_nav("foo")
my_nav("bar")
