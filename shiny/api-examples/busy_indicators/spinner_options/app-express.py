import time

import numpy as np
import seaborn as sns

from shiny.express import input, render, ui

ui.page_opts(title="Busy spinner demo")

ui.busy_indicators.spinner_options(color="orange", size="80px")

with ui.card():
    ui.card_header(
        "Plot that takes a few seconds to render",
        ui.input_task_button("simulate", "Simulate"),
        class_="d-flex justify-content-between align-items-center",
    )

    @render.plot
    def x():
        input.simulate()
        time.sleep(3)
        sns.lineplot(x=np.arange(100), y=np.random.randn(100))


ui.input_select(
    "busy_mode",
    "Busy indicator mode",
    ["spinners", "spinner", "cursor", "none"],
)


@render.express
def busy_mode_ui():
    ui.busy_indicators.mode(input.busy_mode())
