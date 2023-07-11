from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_slider("controller", "Controller", min=0, max=20, value=10),
    ui.input_text("inText", "Input text"),
    ui.input_text("inText2", "Input text 2"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        x = str(input.controller())
        # This will change the value of input$inText, based on x
        ui.update_text("inText", value="New text " + x)
        # Can also set the label, this time for input$inText2
        ui.update_text("inText2", label="New label " + x, value="New text" + x)


app = App(app_ui, server)
