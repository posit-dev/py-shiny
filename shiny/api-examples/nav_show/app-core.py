from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        "Home",
        ui.input_action_button("hideTab", "Hide 'Foo' tab"),
        ui.input_action_button("showTab", "Show 'Foo' tab"),
        ui.input_action_button("hideMenu", "Hide 'More' nav_menu"),
        ui.input_action_button("showMenu", "Show 'More' nav_menu"),
    ),
    ui.navset_tab(
        ui.nav_panel("Foo", "This is the foo tab"),
        ui.nav_panel("Bar", "This is the bar tab"),
        ui.nav_menu(
            "More",
            ui.nav_panel("Table", "Table page"),
            ui.nav_panel("About", "About page"),
            "------",
            "Even more!",
            ui.nav_panel("Email", "Email page"),
            value="More",
        ),
        id="tabs",
    ),
    title="Navbar page",
    id="sidebar",
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect()
    @reactive.event(input.hideTab)
    def _():
        ui.hide_nav_panel("tabs", target="Foo")

    @reactive.effect()
    @reactive.event(input.showTab)
    def _():
        ui.show_nav_panel("tabs", target="Foo")

    @reactive.effect()
    @reactive.event(input.hideMenu)
    def _():
        ui.hide_nav_panel("tabs", target="More")

    @reactive.effect()
    @reactive.event(input.showMenu)
    def _():
        ui.show_nav_panel("tabs", target="More")


app = App(app_ui, server)
