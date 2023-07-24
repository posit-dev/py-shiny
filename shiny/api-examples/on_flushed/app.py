from datetime import datetime

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("flush", "Trigger flush"),
    ui.output_ui("n_clicks"),
    ui.div(id="flush_time"),
)


def server(input: Inputs, output: Outputs, session: Session):
    def log():
        msg = "A reactive flush occurred at " + datetime.now().strftime("%H:%M:%S:%f")
        print(msg)
        ui.insert_ui(
            ui.p(msg),
            selector="#flush_time",
        )

    session.on_flushed(log, once=False)

    @output
    @render.ui
    def n_clicks():
        return "Number of clicks: " + str(input.flush())


app = App(app_ui, server)
