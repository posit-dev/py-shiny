from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_password("password", "Password:"),
    ui.input_action_button("go", "Go"),
    ui.output_text_verbatim("value"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    @reactive.event(input.go)
    def value():
        return input.password()


app = App(app_ui, server)
