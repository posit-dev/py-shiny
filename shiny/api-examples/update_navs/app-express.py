from shiny import reactive
from shiny.express import input, ui

with ui.sidebar():
    ui.input_slider("controller", "Controller", min=1, max=3, value=1)

with ui.navset_card_tab(id="inTabset"):
    with ui.nav_panel("Panel 1", value="panel1"):
        "Panel 1 content"
    with ui.nav_panel("Panel 2", value="panel2"):
        "Panel 2 content"
    with ui.nav_panel("Panel 3", value="panel3"):
        "Panel 3 content"


@reactive.effect
def _():
    ui.update_navs("inTabset", selected="panel" + str(input.controller()))
