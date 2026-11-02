from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_text("text", "Type quickly"),
    ui.output_text("raw"),
    ui.output_text("debounced"),
)


def server(input: Inputs, output: Outputs, session: Session):
    # Update only after typing stops for 1 second
    @reactive.debounce(1)
    @reactive.calc
    def text_debounced():
        return input.text()

    @render.text
    def raw():
        return f"Raw: {input.text()}"

    @render.text
    def debounced():
        return f"Debounced: {text_debounced()}"


app = App(app_ui, server)
