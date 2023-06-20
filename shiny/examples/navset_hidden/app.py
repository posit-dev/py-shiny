from shiny import App, Inputs, Outputs, Session
from shiny import experimental as x
from shiny import reactive, ui

app_ui = x.ui.page_sidebar(
    ui.navset_hidden(
        ui.nav(None, "Panel 1 content", value="panel1"),
        ui.nav(None, "Panel 2 content", value="panel2"),
        ui.nav(None, "Panel 3 content", value="panel3"),
        id="hidden_tabs",
    ),
    sidebar=x.ui.sidebar(
        ui.input_radio_buttons(
            "controller", "Controller", ["1", "2", "3"], selected="1"
        )
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.controller)
    def _():
        ui.update_navs("hidden_tabs", selected="panel" + str(input.controller()))


app = App(app_ui, server)
