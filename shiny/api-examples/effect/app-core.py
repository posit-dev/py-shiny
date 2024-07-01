from shiny import App, Inputs, reactive, ui

app_ui = ui.page_fluid(ui.input_action_button("btn", "Press me!"))


def server(input: Inputs):
    @reactive.effect
    @reactive.event(input.btn)
    def _():
        ui.insert_ui(
            ui.p("Number of clicks: ", input.btn()),
            selector="#btn",
            where="afterEnd",
        )


app = App(app_ui, server)
