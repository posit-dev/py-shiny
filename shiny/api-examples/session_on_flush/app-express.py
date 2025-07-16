from datetime import datetime

from shiny.express import input, render, session, ui

ui.input_action_button("flush", "Trigger flush")


@render.ui
def n_clicks():
    return "Number of clicks: " + str(input.flush())


ui.div(id="flush_time")


def log():
    msg = "A reactive flush occurred at " + datetime.now().strftime("%H:%M:%S:%f")
    print(msg)
    ui.insert_ui(
        ui.p(msg),
        selector="#flush_time",
    )


if hasattr(session, "on_flush"):
    _ = session.on_flush(log, once=False)
