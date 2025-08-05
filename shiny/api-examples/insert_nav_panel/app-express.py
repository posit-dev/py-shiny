from shiny import reactive
from shiny.express import input, ui

with ui.sidebar():
    ui.input_action_button("add", "Add 'Dynamic' tab")
    ui.input_action_button("update_foo", "Add/Remove 'Foo' tab")


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


@reactive.effect
@reactive.event(input.update_foo)
def _():
    if input.update_foo() % 2 == 0:
        ui.insert_nav_panel(
            "tabs",
            "Foo",
            "Foo is back now",
            value="Foo",
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
    ui.insert_nav_panel("tabs", title=id, value=id, target="s2", position="before")
    ui.notification_show(f"Added tab to menu: {id}")
