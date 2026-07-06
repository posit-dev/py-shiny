import time

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_submit_textarea("text", placeholder="Enter some input..."),
    ui.output_text("value"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def value():
        if "text" in input:
            # Simulate processing time
            time.sleep(2)
            return f"You entered: {input.text()}"
        else:
            return "Submit some input to see it here."


app = App(app_ui, server)
