from shiny import reactive
from shiny.express import input, ui

with ui.layout_sidebar():
    with ui.sidebar(title="Navbar page", id="sidebar"):
        "Home"
        ui.input_action_button("hideTab", "Hide 'Foo' tab")
        ui.input_action_button("showTab", "Show 'Foo' tab")
        ui.input_action_button("hideMenu", "Hide 'More' nav_menu")
        ui.input_action_button("showMenu", "Show 'More' nav_menu")

    with ui.navset_tab(id="tabs"):
        with ui.nav_panel("Foo", value="Foo"):
            "This is the foo tab"
        with ui.nav_panel("Bar", value="Bar"):
            "This is the bar tab"
        with ui.nav_menu(title="More", value="More"):
            with ui.nav_panel("Table"):
                "Table page"
            with ui.nav_panel("About"):
                "About page"
            "------"
            "Even more!"
            with ui.nav_panel("Email"):
                "Email page"

    @reactive.effect
    @reactive.event(input.hideTab)
    def _():
        ui.update_nav_panel("tabs", target="Foo", method="hide")

    @reactive.effect
    @reactive.event(input.showTab)
    def _():
        ui.update_nav_panel("tabs", target="Foo", method="show")

    @reactive.effect
    @reactive.event(input.hideMenu)
    def _():
        ui.update_nav_panel("tabs", target="More", method="hide")

    @reactive.effect
    @reactive.event(input.showMenu)
    def _():
        ui.update_nav_panel("tabs", target="More", method="show")
