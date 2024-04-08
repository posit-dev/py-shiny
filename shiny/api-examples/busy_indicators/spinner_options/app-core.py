import time

import numpy as np
import seaborn as sns

from shiny import App, render, ui

app_ui = ui.page_fixed(
    ui.h4("Busy spinner demo"),
    ui.busy_indicators.spinner_options(color="orange", size="80px"),
    ui.card(
        ui.card_header(
            "Plot that takes a few seconds to render",
            ui.input_task_button("simulate", "Simulate"),
            class_="d-flex justify-content-between align-items-center",
        ),
        ui.output_plot("plot"),
    ),
    ui.input_select(
        "busy_mode",
        "Busy indicator mode",
        ["spinners", "spinner", "cursor", "none"],
    ),
    ui.output_ui("busy_mode_ui"),
)


def server(input):

    @render.plot
    def plot():
        input.simulate()
        time.sleep(3)
        sns.lineplot(x=np.arange(100), y=np.random.randn(100))

    @render.ui
    def busy_mode_ui():
        ui.busy_indicators.mode(input.busy_mode())


app = App(app_ui, server)
