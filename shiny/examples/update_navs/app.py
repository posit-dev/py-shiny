from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fixed(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_slider("controller", "Controller", min=1, max=3, value=1)
        ),
        ui.panel_main(
            ui.navset_tab_card(
                ui.nav("Panel 1", "Panel 1 content", value="panel1"),
                ui.nav("Panel 2", "Panel 2 content", value="panel2"),
                ui.nav("Panel 3", "Panel 3 content", value="panel3"),
                id="inTabset",
            ),
        ),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        ui.update_navs("inTabset", selected="panel" + str(input.controller()))


app = App(app_ui, server)
