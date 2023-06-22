from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(ui.input_action_button("btn", "Press me!"))


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.btn)
    def _():
        ui.insert_ui(
            ui.p("Number of clicks: ", input.btn()), selector="#btn", where="afterEnd"
        )


app = App(app_ui, server)
