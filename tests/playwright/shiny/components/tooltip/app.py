from shiny import App, Inputs, Outputs, Session, reactive, req, ui

app_ui = ui.page_fluid(
    ui.input_action_button("btn_show", "Show tooltip", class_="mt-3 me-3"),
    ui.input_action_button("btn_close", "Close tooltip", class_="mt-3 me-3"),
    ui.br(),
    ui.br(),
    ui.tooltip(
        ui.input_action_button("btn_w_tooltip", "A button w/ a tooltip", class_="mt-3"),
        "A message",
        id="tooltip_id",
        placement="right",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    def _():
        req(input.btn_show())

        ui.update_tooltip("tooltip_id", show=True)

    @reactive.effect
    def _():
        req(input.btn_close())

        ui.update_tooltip("tooltip_id", show=False)

    @reactive.effect
    def _():
        req(input.btn_w_tooltip())
        ui.notification_show("Button clicked!", duration=3, type="message")


app = App(app_ui, server=server)
