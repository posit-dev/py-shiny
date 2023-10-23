from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("btn_update", "Update tooltip phrase", class_="mt-3 me-3"),
    ui.br(),
    ui.br(),
    ui.tooltip(
        ui.input_action_button("btn_w_tooltip", "A button w/ a tooltip", class_="mt-3"),
        "A message",
        id="tooltip_id",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        # Immediately display tooltip
        ui.toggle_tooltip("tooltip_id", show=True)

    @reactive.Effect
    @reactive.event(input.btn_update)
    def _():
        content = (
            "A " + " ".join(["NEW" for _ in range(input.btn_update())]) + " message"
        )

        ui.update_tooltip("tooltip_id", content)
        ui.toggle_tooltip("tooltip_id", show=True)

    @reactive.Effect
    @reactive.event(input.btn_w_tooltip)
    def _():
        ui.notification_show("Button clicked!", duration=3, type="message")


app = App(app_ui, server=server)
