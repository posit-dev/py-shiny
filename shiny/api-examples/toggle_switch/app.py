from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_switch("switch_value", label="Switch"),
    ui.input_action_button(
        "toggle_btn",
        label="Toggle the switch",
        width="fit-content",
    ),
    ui.output_text_verbatim("state"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.toggle_btn)
    def _():
        ui.toggle_switch("switch_value")

    @output
    @render.text
    def state():
        return f"input.switch(): {input.switch_value()}"


app = App(app_ui, server=server)
