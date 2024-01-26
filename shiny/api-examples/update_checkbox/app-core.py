from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_slider("controller", "Controller", min=0, max=1, value=0, step=1),
    ui.input_checkbox("inCheckbox", "Input checkbox"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        # True if controller is odd, False if even.
        x_even = input.controller() % 2 == 1
        ui.update_checkbox("inCheckbox", value=x_even)


app = App(app_ui, server)
