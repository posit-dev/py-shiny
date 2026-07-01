from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.offcanvas(
        ui.p("Panel via trigger."),
        title="Trigger Panel",
        id="trigger_panel",
        trigger=ui.input_action_button("open_btn", "Open"),
    ),
    ui.br(),
    ui.input_action_button("show_btn", "Show"),
    ui.input_action_button("hide_btn", "Hide"),
    ui.offcanvas(
        ui.p("Panel via server."),
        title="Server Panel",
        id="server_panel",
    ),
    ui.br(),
    ui.output_text_verbatim("trigger_state"),
    ui.output_text_verbatim("server_state"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.show_btn)
    def _():
        ui.toggle_offcanvas("server_panel", show=True)

    @reactive.effect
    @reactive.event(input.hide_btn)
    def _():
        ui.toggle_offcanvas("server_panel", show=False)

    @render.text
    def trigger_state():
        return "open" if input.trigger_panel() else "closed"

    @render.text
    def server_state():
        return "open" if input.server_panel() else "closed"


app = App(app_ui, server=server)
