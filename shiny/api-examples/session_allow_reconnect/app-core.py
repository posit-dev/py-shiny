from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Session Reconnection Control"),
    ui.p(
        """
        This example demonstrates the session.allow_reconnect() method. 
        Click a button to set the reconnection behavior, then you can test it 
        by simulating a disconnect (e.g., close the browser tab and reopen it, 
        or use browser developer tools to close the WebSocket connection).
        """
    ),
    ui.layout_columns(
        ui.input_action_button("allow_true", "Allow Reconnect"),
        ui.input_action_button("allow_false", "Disallow Reconnect"),
        ui.input_action_button("allow_force", "Force Reconnect"),
        col_widths=[4, 4, 4],
    ),
    ui.output_text("status"),
)


def server(input: Inputs, output: Outputs, session: Session):
    status = reactive.Value("Reconnection not configured yet")

    @reactive.effect
    @reactive.event(input.allow_true)
    def _():
        session.allow_reconnect(True)
        status.set("✓ Reconnection allowed (True)")

    @reactive.effect
    @reactive.event(input.allow_false)
    def _():
        session.allow_reconnect(False)
        status.set("✗ Reconnection disallowed (False)")

    @reactive.effect
    @reactive.event(input.allow_force)
    def _():
        session.allow_reconnect("force")
        status.set("⚡ Reconnection forced")

    @output
    @render.text
    def status():
        return status.get()


app = App(app_ui, server)
