from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_sidebar(
    ui.sidebar(ui.input_slider("controller", "Controller", min=1, max=3, value=1)),
    ui.navset_card_tab(
        ui.nav_panel("Panel 1", "Panel 1 content", value="panel1"),
        ui.nav_panel("Panel 2", "Panel 2 content", value="panel2"),
        ui.nav_panel("Panel 3", "Panel 3 content", value="panel3"),
        id="inTabset",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    def _():
        ui.update_navset("inTabset", selected="panel" + str(input.controller()))


app = App(app_ui, server)
