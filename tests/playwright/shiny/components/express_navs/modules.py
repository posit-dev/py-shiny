from shiny import reactive
from shiny.express import ui, module


@module
def add_to_counter_content(
    input, output, session, _on_click, starting_value, label="Add to Counter"
):
    count = reactive.value(starting_value)
    ui.input_action_button("add", label)

    @reactive.effect
    @reactive.event(input.add)
    def increment_button():
        _on_click()
        count.set(count() + 1)


@module
def custom_sidebar(
    input, output, session, _on_click, starting_value=0, label="Dynamic Sidebar"
):
    count = reactive.value(starting_value)

    @reactive.effect
    @reactive.event(input.addFoo)
    def increment_button():
        _on_click()
        count.set(count() + 1)

    with ui.sidebar():
        ui.input_action_button("add", "Add 'Dynamic' tab")
        ui.input_action_button("removeFoo", "Remove 'Foo' tabs")
        ui.input_action_button("addFoo", "Add New 'Foo' tab")

        @reactive.effect()
        @reactive.event(input.removeFoo)
        def _():
            ui.remove_nav_panel("tabs", target="Foo")

        @reactive.effect()
        @reactive.event(input.addFoo)
        def _():
            n = str(input.addFoo())
            ui.insert_nav_panel(
                "tabs",
                "Foo-" + n,
                "This is the new Foo-" + n + " tab",
                value="Foo",
                target="Menu",
                position="before",
                select=True,
            )

    with ui.navset_tab(id="tabs"):
        with ui.nav_panel("Hello", value="Hello"):
            "This is the hello tab"
        with ui.nav_panel("Foo", value="Foo"):
            "This is the Foo tab"
        with ui.nav_menu("Static", value="Menu"):
            with ui.nav_panel("Static 1", value="s1"):
                "Static 1"
            with ui.nav_panel("Static 2", value="s2"):
                "Static 2"

    @reactive.effect()
    @reactive.event(input.add)
    def _():
        id = "Dynamic-" + str(input.add())
        ui.insert_nav_panel("tabs", title=id, value=id, target="s2", position="before")
