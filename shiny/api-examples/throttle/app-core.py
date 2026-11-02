from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_text("text", "Type quickly"),
    ui.output_text("raw"),
    ui.output_text("throttled"),
)


def server(input: Inputs, output: Outputs, session: Session):
    # Update at most once per second
    @reactive.throttle(1)
    @reactive.calc
    def text_throttled():
        return input.text()

    @render.text
    def raw():
        return f"Raw: {input.text()}"

    @render.text
    def throttled():
        return f"Throttled: {text_throttled()}"


app = App(app_ui, server)
