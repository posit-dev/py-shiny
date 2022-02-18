from shiny import *

app_ui = ui.page_fluid(
    ui.input_action_button("btn", "Press me to print to the Python console!")
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect()
    def _():
        print("Button pressed! " + str(input.btn()))


app = App(app_ui, server)
