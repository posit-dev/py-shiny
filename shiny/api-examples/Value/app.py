from shiny import App, Inputs, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("minus", "-1"),
    " ",
    ui.input_action_button("plus", "+1"),
    ui.br(),
    ui.output_text("value"),
)


def server(input: Inputs):
    val = reactive.Value(0)

    @reactive.Effect
    @reactive.event(input.minus)
    def _():
        newVal = val.get() - 1
        val.set(newVal)

    @reactive.Effect
    @reactive.event(input.plus)
    def _():
        newVal = val.get() + 1
        val.set(newVal)

    @render.text
    def value():
        return str(val.get())


app = App(app_ui, server)
