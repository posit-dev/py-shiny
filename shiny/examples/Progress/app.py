from shiny import *

app_ui = ui.page_fluid(
    ui.input_action_button("button", "Compute"),
    ui.output_text("compute"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    @reactive.event(input.button)
    def compute():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            import time

            for i in range(1, 15):
                p.set(i, message="Computing")
                time.sleep(0.1)

        return "Done computing!"


app = App(app_ui, server)
