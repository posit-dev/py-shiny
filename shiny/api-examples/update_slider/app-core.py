from shiny import App, reactive, ui

app_ui = ui.page_fixed(
    ui.input_slider(
        "receiver", "Receiver:", min=0, max=100, value=50, step=1, width="100%"
    ),
    ui.p(
        "Change the min and max values below to see the receiver slider above update."
    ),
    ui.layout_column_wrap(
        ui.input_slider("min", "Min:", min=0, max=50, value=0, step=1),
        ui.input_slider("max", "Max:", min=50, max=100, value=100, step=1),
        width=1 / 2,
    ),
)


def server(input, output, session):
    @reactive.effect
    def _():
        # You can update the value, min, max, and step.
        ui.update_slider(
            "receiver",
            value=max(min(input.receiver(), input.max()), input.min()),
            min=input.min(),
            max=input.max(),
        )


app = App(app_ui, server)
