from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_fluid(
    ui.input_checkbox("show", "Show radio buttons", False),
    ui.panel_conditional(
        "input.show", ui.input_radio_buttons("radio", "Choose ", ["slider", "select"])
    ),
    ui.panel_conditional(
        "input.show && input.radio === 'slider'",
        ui.input_slider("slider", None, min=0, max=100, value=50),
    ),
    ui.panel_conditional(
        "input.show && input.radio === 'select'",
        ui.input_select("slider", None, ["A", "B", "C"]),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
