from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.offcanvas(
        ui.p("This is the offcanvas body content."),
        title="Details",
        id="panel",
    ),
    ui.input_action_button("toggle_btn", "Toggle panel"),
    ui.input_action_button("hide_btn", "Hide panel"),
    ui.br(),
    ui.br(),
    ui.output_text_verbatim("state"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.toggle_btn)
    def _():
        ui.toggle_offcanvas("panel")

    @reactive.effect
    @reactive.event(input.hide_btn)
    def _():
        ui.hide_offcanvas("panel")

    @render.text
    def state():
        return f"Panel is {'open' if input.panel() else 'closed'}"


app = App(app_ui, server=server)
