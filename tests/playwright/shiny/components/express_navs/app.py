from shiny import reactive
from shiny.express import render
from .modules import custom_sidebar, add_to_counter_content

tabs_added = reactive.value(0)


def increment_tabs_counter():
    tabs_added.set(tabs_added() + 1)


custom_sidebar(
    "nav",
    _on_click=increment_tabs_counter,
    label="Dynamic Sidebar",
)

add_to_counter_content(
    "buttonAdder",
    _on_click=increment_tabs_counter,
    starting_value=0,
    label="Add to Counter",
)


@render.code
def out():
    return f"Tabs added: {tabs_added()}"
