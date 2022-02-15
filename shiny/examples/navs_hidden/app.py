from shiny import *

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_radio_buttons("controller", "Controller", ["1", "2", "3"], "1")
        ),
        ui.panel_main(
            ui.navs_hidden(
                ui.nav_content("panel1", "Panel 1 content"),
                ui.nav_content("panel2", "Panel 2 content"),
                ui.nav_content("panel3", "Panel 3 content"),
                id="hidden_tabs",
            )
        )
    )
)

def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect()
    @event(input.controller)
    def _():
        ui.update_navs("hidden_tabs", selected="panel" + str(input.controller()))


app = App(app_ui, server)
