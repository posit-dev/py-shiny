import time

import numpy as np
import seaborn as sns

from shiny import App, render, ui

app_ui = ui.page_fixed(
    ui.h4("Busy spinner demo", class_="pt-3"),
    ui.busy_indicators.spinner_options(color="orange", size="80px"),
    ui.card(
        ui.card_header(
            "Plot that takes a few seconds to render",
            ui.input_task_button("simulate", "Simulate"),
            class_="d-flex justify-content-between align-items-center",
        ),
        ui.output_plot("plot"),
    ),
    ui.input_selectize(
        "indicator_types",
        "Busy indicator types",
        ["spinners", "pulse", "cursor"],
        multiple=True,
        selected=["spinners", "pulse"],
    ),
    ui.output_ui("indicator_types_ui"),
)


def server(input):

    @render.plot
    def plot():
        input.simulate()
        time.sleep(3)
        sns.lineplot(x=np.arange(100), y=np.random.randn(100))

    @render.ui
    def indicator_types_ui():
        return ui.busy_indicators.use(input.indicator_types())


app = App(app_ui, server)
