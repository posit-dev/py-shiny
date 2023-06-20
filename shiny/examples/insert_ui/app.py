from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("add", "Add UI"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.add)
    def _():
        ui.insert_ui(
            ui.input_text("txt" + str(input.add()), "Enter some text"),
            selector="#add",
            where="afterEnd",
        )


app = App(app_ui, server)
