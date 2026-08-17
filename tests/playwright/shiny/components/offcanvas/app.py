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
    ui.offcanvas(
        ui.p("Panel via server."),
        ui.input_action_button("hide_btn", "Hide"),
        title="Server Panel",
        id="server_panel",
    ),
    ui.br(),
    ui.output_code("trigger_state"),
    ui.output_code("server_state"),
    ui.offcanvas(
        ui.p("Panel declared for id-based reveal."),
        title="Existing Panel",
        id="existing_panel",
    ),
    ui.br(),
    ui.input_action_button("show_existing_btn", "Show existing (by id)"),
    ui.input_action_button("show_content_btn", "Show wrapped content"),
    ui.input_action_button("show_bad_id_btn", "Show bad id"),
    ui.output_text("bad_id_error"),
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

    @render.code
    def trigger_state():
        return "open" if input.trigger_panel() else "closed"

    @render.code
    def server_state():
        return "open" if input.server_panel() else "closed"

    @reactive.effect
    @reactive.event(input.show_existing_btn)
    def _():
        # str dispatch: reveals the panel already declared in the UI, by id.
        ui.show_offcanvas("existing_panel")

    @reactive.effect
    @reactive.event(input.show_content_btn)
    def _():
        # TagChild dispatch: wraps bare content into a new anonymous panel.
        ui.show_offcanvas(ui.p("Wrapped content panel."))

    bad_id_error_val = reactive.value("")

    @reactive.effect
    @reactive.event(input.show_bad_id_btn)
    def _():
        try:
            ui.show_offcanvas("bad id with spaces")
        except ValueError as e:
            bad_id_error_val.set(str(e))

    @render.text
    def bad_id_error():
        return bad_id_error_val()


app = App(app_ui, server=server)
