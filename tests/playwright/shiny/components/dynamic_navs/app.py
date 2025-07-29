from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_action_button("add", "Add 'Dynamic' tab"),
        ui.input_action_button("removeFoo", "Remove 'Foo' tabs"),
        ui.input_action_button("addFoo", "Add New 'Foo' tab"),
        ui.input_action_button("hideTab", "Hide 'Foo' tab"),
        ui.input_action_button("showTab", "Show 'Foo' tab"),
        ui.input_action_button("hideMenu", "Hide 'Static' nav_menu"),
        ui.input_action_button("showMenu", "Show 'Static' nav_menu"),
    ),
    ui.navset_tab(
        ui.nav_panel("Hello", "This is the hello tab", value="Hello"),
        ui.nav_panel("Foo", "This is the Foo tab", value="Foo"),
        ui.nav_menu(
            "Menu",
            ui.nav_panel("Static1", "Static1", value="s1"),
            ui.nav_panel("Static2", "Static2", value="s2"),
            value="Menu",
        ),
        id="tabs",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):

    @reactive.effect
    def _():
        ui.insert_nav_panel(
            "tabs",
            "Stringy Panel",
            target="Foo",
            position="before",
        )
        ui.insert_nav_panel(
            "tabs",
            "Stringier Panel",
            target="s2",
            position="before",
        )

    @reactive.effect
    @reactive.event(input.add)
    def _():
        id = "Dynamic-" + str(input.add())
        ui.insert_nav_panel(
            "tabs",
            ui.nav_panel(id, id),
            target="s2",
            position="before",
        )

    @reactive.effect
    @reactive.event(input.removeFoo)
    def _():
        ui.remove_nav_panel("tabs", target="Foo")

    @reactive.effect
    @reactive.event(input.addFoo)
    def _():
        n = str(input.addFoo())
        ui.insert_nav_panel(
            "tabs",
            ui.nav_panel("Foo-" + n, "Foo-" + n, value="Foo"),
            target="Menu",
            position="before",
            select=True,
        )

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
        ui.update_nav_panel("tabs", target="Menu", method="hide")

    @reactive.effect
    @reactive.event(input.showMenu)
    def _():
        ui.update_nav_panel("tabs", target="Menu", method="show")


app = App(app_ui, server)
