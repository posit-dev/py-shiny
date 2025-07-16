from shiny import *

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_action_button("add", "Add 'Dynamic' tab"),
            ui.input_action_button("removeFoo", "Remove 'Foo' tabs"),
            ui.input_action_button("addFoo", "Add New 'Foo' tab"),
        ),
        ui.panel_main(
            ui.navset_tab(
                ui.nav("Hello", "This is the hello tab"),
                ui.nav("Foo", "This is the Foo tab", value="Foo"),
                ui.nav_menu(
                    "Static",
                    ui.nav("Static 1", "Static 1", value="s1"),
                    ui.nav("Static 2", "Static 2", value="s2"),
                    value="Menu",
                ),
                id="tabs",
            ),
        ),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect()
    @event(input.add)
    def _():
        id = "Dynamic-" + str(input.add())
        ui.nav_insert(
            "tabs",
            ui.nav(id, id),
            target="s2",
            position="before",
        )

    @reactive.Effect()
    @event(input.removeFoo)
    def _():
        ui.nav_remove("tabs", target="Foo")

    @reactive.Effect()
    @event(input.addFoo)
    def _():
        n = str(input.addFoo())
        ui.nav_insert(
            "tabs",
            ui.nav("Foo-" + n, "This is the new Foo-" + n + " tab", value="Foo"),
            target="Menu",
            position="before",
            select=True,
        )


app = App(app_ui, server)
