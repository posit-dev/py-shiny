from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_slider("controller", "Controller", min=0, max=20, value=10),
    ui.input_numeric("inNumber", "Input number", 0),
    ui.input_numeric("inNumber2", "Input number 2", 0),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        x = input.controller()
        ui.update_numeric("inNumber", value=x)
        ui.update_numeric(
            "inNumber2",
            label="Number label " + str(x),
            value=x,
            min=x - 10,
            max=x + 10,
            step=5,
        )


app = App(app_ui, server)
