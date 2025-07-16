from shiny import *

app_ui = ui.page_navbar(
    ui.nav(
        "Home",
        ui.input_action_button("hideTab", "Hide 'Foo' tab"),
        ui.input_action_button("showTab", "Show 'Foo' tab"),
        ui.input_action_button("hideMenu", "Hide 'More' nav_menu"),
        ui.input_action_button("showMenu", "Show 'More' nav_menu"),
    ),
    ui.nav("Foo", "This is the foo tab"),
    ui.nav("Bar", "This is the bar tab"),
    ui.nav_menu(
        "More",
        ui.nav("Table", "Table page"),
        ui.nav("About", "About page"),
        "------",
        "Even more!",
        ui.nav("Email", "Email page"),
    ),
    title="Navbar page",
    id="tabs",
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect()
    @event(input.hideTab)
    def _():
        ui.nav_hide("tabs", target="Foo")

    @reactive.Effect()
    @event(input.showTab)
    def _():
        ui.nav_show("tabs", target="Foo")

    @reactive.Effect()
    @event(input.hideMenu)
    def _():
        ui.nav_hide("tabs", target="More")

    @reactive.Effect()
    @event(input.showMenu)
    def _():
        ui.nav_show("tabs", target="More")


app = App(app_ui, server)
