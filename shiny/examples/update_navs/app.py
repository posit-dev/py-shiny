from shiny import App, Inputs, Outputs, Session
from shiny import experimental as x
from shiny import reactive, ui

app_ui = x.ui.page_sidebar(
    ui.navset_tab_card(
        ui.nav("Panel 1", "Panel 1 content", value="panel1"),
        ui.nav("Panel 2", "Panel 2 content", value="panel2"),
        ui.nav("Panel 3", "Panel 3 content", value="panel3"),
        id="inTabset",
    ),
    sidebar=x.ui.sidebar(
        ui.input_slider("controller", "Controller", min=1, max=3, value=1)
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        ui.update_navs("inTabset", selected="panel" + str(input.controller()))


app = App(app_ui, server)
