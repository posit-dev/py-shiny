from shiny import App, Inputs, Outputs, Session, reactive, req, ui

app_ui = ui.page_fluid(
    ui.input_action_button("btn_update", "Update popover phrase", class_="mt-3 me-3"),
    ui.br(),
    ui.br(),
    ui.popover(
        ui.input_action_button("btn_w_popover", "A button w/ a popover", class_="mt-3"),
        "A message",
        id="popover_id",
        title="To start",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    def _():
        # Immediately display popover
        ui.update_popover("popover_id", show=True)

    @reactive.effect
    @reactive.event(input.btn_update)
    def _():
        content = (
            "A " + " ".join(["NEW" for _ in range(input.btn_update())]) + " message"
        )

        ui.update_popover(
            "popover_id",
            content,
            # #   Causes bug. Skipping for now
            #   show=True
        )

    @reactive.effect
    def _():
        req(input.btn_w_popover())
        ui.notification_show("Button clicked!", duration=3, type="message")


app = App(app_ui, server=server)
