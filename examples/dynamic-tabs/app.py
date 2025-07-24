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
        ui.nav_panel("Hello", "This is the hello tab"),
        ui.nav_panel("Foo", "This is the Foo tab", value="Foo"),
        ui.nav_menu(
            "Static",
            ui.nav_panel("Static 1", "Static 1", value="s1"),
            ui.nav_panel("Static 2", "Static 2", value="s2"),
            value="Menu",
        ),
        id="tabs",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect()
    @reactive.event(input.add)
    def _():
        id = "Dynamic-" + str(input.add())
        ui.nav_insert(
            "tabs",
            ui.nav_panel(id, id),
            target="s2",
            position="before",
        )

    @reactive.effect()
    @reactive.event(input.removeFoo)
    def _():
        ui.nav_remove("tabs", target="Foo")

    @reactive.effect()
    @reactive.event(input.addFoo)
    def _():
        n = str(input.addFoo())
        ui.nav_insert(
            "tabs",
            ui.nav_panel("Foo-" + n, "This is the new Foo-" + n + " tab", value="Foo"),
            target="Menu",
            position="before",
            select=True,
        )

    @reactive.effect()
    @reactive.event(input.hideTab)
    def _():
        ui.nav_hide("tabs", target="Foo")

    @reactive.effect()
    @reactive.event(input.showTab)
    def _():
        ui.nav_show("tabs", target="Foo")

    @reactive.effect()
    @reactive.event(input.hideMenu)
    def _():
        ui.nav_hide("tabs", target="Menu")

    @reactive.effect()
    @reactive.event(input.showMenu)
    def _():
        ui.nav_show("tabs", target="Menu")


app = App(app_ui, server)
