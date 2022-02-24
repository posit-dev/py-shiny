from datetime import datetime
from shiny import *

app_ui = ui.page_fluid(
    ui.input_action_button("flush", "Trigger flush"),
    "See the python console for log events",
    ui.output_ui("n_clicks"),
)


def server(input: Inputs, output: Outputs, session: Session):
    def log():
        print("Finished flushing at " + datetime.now().strftime("%H:%M:%S"))

    session.on_flushed(log, once=False)

    @output()
    @render_ui()
    def n_clicks():
        n = input.flush()
        return "Number of clicks: " + str(n)


app = App(app_ui, server)
