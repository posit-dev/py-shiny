from shiny import reactive
from shiny.express import input, ui

ui.input_radio_buttons("controller1", "Controller1", ["1", "2", "3"], selected="2")

with ui.navset_hidden(
    id="hidden_tabs1",
    header=ui.tags.div("Navset_hidden_header", id="navset_hidden_header1"),
    footer=ui.tags.div("Navset_hidden_footer", id="navset_hidden_footer1"),
    selected="panel2",
):
    with ui.nav_panel(None, value="panel1"):
        "Panel 1 content"
    with ui.nav_panel(None, value="panel2"):
        "Panel 2 content"
    with ui.nav_panel(None, value="panel3"):
        "Panel 3 content"

ui.markdown("-----")
ui.input_radio_buttons("controller2", "Controller2", ["4", "5", "6"])

with ui.navset_hidden(id="hidden_tabs2"):
    with ui.nav_panel(None, value="panel4"):
        "Panel 4 content"
    with ui.nav_panel(None, value="panel5"):
        "Panel 5 content"
    with ui.nav_panel(None, value="panel6"):
        "Panel 6 content"


@reactive.effect
@reactive.event(input.controller1)
def _():
    ui.update_navs("hidden_tabs1", selected="panel" + str(input.controller1()))


@reactive.effect
@reactive.event(input.controller2)
def _():
    ui.update_navs("hidden_tabs2", selected="panel" + str(input.controller2()))
