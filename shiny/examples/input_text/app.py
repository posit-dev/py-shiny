from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_text("caption", "Caption:", "Data summary"),
    ui.output_text_verbatim("value"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    def value():
        return input.caption()


app = App(app_ui, server)
