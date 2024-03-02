from shiny import reactive
from shiny.express import input, ui

with ui.sidebar():
    ui.input_radio_buttons("controller", "Controller", ["1", "2", "3"], selected="1")

with ui.navset_hidden(id="hidden_tabs"):
    with ui.nav_panel(None, value="panel1"):
        "Panel 1 content"
    with ui.nav_panel(None, value="panel2"):
        "Panel 2 content"
    with ui.nav_panel(None, value="panel3"):
        "Panel 3 content"


@reactive.effect
@reactive.event(input.controller)
def _():
    ui.update_navs("hidden_tabs", selected="panel" + str(input.controller()))
