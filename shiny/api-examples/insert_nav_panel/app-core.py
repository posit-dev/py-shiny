from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_action_button("add", "Add 'Dynamic' tab"),
        ui.input_action_button("remove_foo", "Remove 'Foo' tabs"),
        ui.input_action_button("add_foo", "Add New 'Foo' tab"),
        # Add text panels adds both a text panel in the main navset as well as one in the menu dropdown
        ui.input_action_button("add_text_panel", "Add Text Panels"),
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
    @reactive.event(input.remove_foo)
    def _():
        ui.remove_nav_panel("tabs", target="Foo")

    @reactive.effect
    @reactive.event(input.add_foo)
    def _():
        n = str(input.add_foo())
        ui.insert_nav_panel(
            "tabs",
            ui.nav_panel("Foo-" + n, "This is the new Foo-" + n + " tab", value="Foo"),
            target="Menu",
            position="before",
            select=True,
        )

    # Button push for add_text_panel adds two panels

    @reactive.effect
    @reactive.event(input.add_text_panel)
    def _():
        id = "Text-" + str(input.add_text_panel())
        ui.insert_nav_panel(
            "tabs",
            id,
            target="s2",
            position="before",
        )

    @reactive.effect
    @reactive.event(input.add_text_panel)
    def _():
        ui.insert_nav_panel(
            "tabs",
            "Placeholder Text Panel",
            target="Menu",
            position="before",
            select=True,
        )


app = App(app_ui, server)
