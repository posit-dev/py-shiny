from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_action_button("add", "Add 'Dynamic' tab"),
        ui.input_action_button("update_foo", "Add/Remove 'Foo' tab"),
    ),
    ui.navset_tab(
        ui.nav_panel("Hello", "This is the hello tab", value="Hello"),
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

    @reactive.effect
    @reactive.event(input.update_foo)
    def _():
        if input.update_foo() % 2 == 0:
            ui.insert_nav_panel(
                "tabs",
                ui.nav_panel("Foo", "Foo is back now", value="Foo"),
                target="Menu",
                position="before",
                select=True,
            )
        else:
            ui.remove_nav_panel("tabs", target="Foo")

    @reactive.effect
    @reactive.event(input.add)
    def _():
        id = "Dynamic-" + str(input.add())
        ui.insert_nav_panel(
            "tabs",
            ui.nav_panel(id, id, value=id),
            target="s2",
            position="before",
        )

        ui.notification_show(f"Added tab to menu: {id}")


app = App(app_ui, server)
