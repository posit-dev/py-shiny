from shiny import *

app_ui = ui.page_fluid(
    ui.output_text("compute"),
    ui.input_action_button("button", "Compute"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output()
    @render_text()
    def compute():
        p = ui.Progress(min=1, max=15)
        p.set(message="Calculation in progress", detail="This may take a while...")

        import time

        for i in range(1, 15):
            p.set(i, message="Computing")
            time.sleep(0.1)

        p.close()

        return "Done computing!"


app = App(app_ui, server)
