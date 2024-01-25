from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.tags.p("The first slider controls the second"),
        ui.input_slider("control", "Controller:", min=0, max=20, value=10, step=1),
        ui.input_slider("receive", "Receiver:", min=0, max=20, value=10, step=1),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        val = input.control()
        # Control the value, min, max, and step.
        # Step size is 2 when input value is even; 1 when value is odd.
        ui.update_slider(
            "receive", value=val, min=int(val / 2), max=val + 4, step=(val + 1) % 2 + 1
        )


app = App(app_ui, server)
