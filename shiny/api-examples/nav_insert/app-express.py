from shiny import reactive
from shiny.express import input, ui

with ui.layout_sidebar():
    with ui.sidebar():
        ui.input_action_button("add", "Add 'Dynamic' tab")
        ui.input_action_button("removeFoo", "Remove 'Foo' tabs")
        ui.input_action_button("addFoo", "Add New 'Foo' tab")

    with ui.navset_tab(id="set"):
        with ui.nav_panel("Hello", value="Hello"):
            "This is the hello tab"
        with ui.nav_panel("Foo", value="Foo"):
            "This is the Foo tab"
        with ui.nav_menu("Static", value="tabs"):
            with ui.nav_panel("Static 1", value="s1"):
                "Static 1"
            with ui.nav_panel("Static 2", value="s2"):
                "Static 2"

    @reactive.effect()
    @reactive.event(input.add)
    def _():
        id = "Dynamic-" + str(input.add())
        with ui.hold() as new_panel:
            with ui.nav_panel(id, value=id):
                pass
        ui.nav_insert(
            "tabs",
            new_panel,
            target="s2",
            position="before",
        )

    @reactive.effect()
    @reactive.event(input.removeFoo)
    def _():
        ui.nav_remove("set", target="Foo")

    @reactive.effect()
    @reactive.event(input.addFoo)
    def _():
        n = str(input.addFoo())
        with ui.hold() as new_panel:
            with ui.nav_panel("Foo-" + n, value="Foo"):
                "This is the new Foo-" + n + " tab"
        ui.nav_insert(
            "tabs",
            new_panel[0],
            target="Menu",
            position="before",
            select=True,
        )
