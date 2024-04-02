from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_action_button("minus", "-1"),
        ui.input_action_button("plus", "+1"),
    ),
    ui.output_text("value"),
)


def server(input: Inputs, output: Outputs, session: Session):
    val = reactive.value(0)

    @reactive.effect
    @reactive.event(input.minus)
    def _():
        newVal = val.get() - 1
        val.set(newVal)

    @reactive.effect
    @reactive.event(input.plus)
    def _():
        newVal = val.get() + 1
        val.set(newVal)

    @render.text
    def value():
        return str(val.get())


app = App(app_ui, server)
