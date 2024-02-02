from shiny import reactive
from shiny.express import input, render, ui

with ui.sidebar(id="sidebar"):
    "Sidebar content"

ui.input_action_button("open_sidebar", label="Open sidebar", class_="me-3")
ui.input_action_button("close_sidebar", label="Close sidebar", class_="me-3")


@render.text
def state():
    return f"input.sidebar(): {input.sidebar()}"


@reactive.effect
@reactive.event(input.open_sidebar)
def _():
    ui.update_sidebar("sidebar", show=True)


@reactive.effect
@reactive.event(input.close_sidebar)
def _():
    ui.update_sidebar("sidebar", show=False)
