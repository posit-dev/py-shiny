from shiny import *

app_ui = ui.page_fluid(ui.input_action_button("btn", "Press me!"))


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @event(input.btn)
    def _():
        ui.insert_ui(
            ui.p("Number of clicks: ", input.btn()), selector="#btn", where="afterEnd"
        )


app = App(app_ui, server)
