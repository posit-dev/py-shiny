import os
import time

import numpy as np
import seaborn as sns

from shiny.express import input, render, ui

ui.page_opts(title="Busy spinner demo")

with ui.sidebar():
    ui.input_selectize(
        "indicator_types",
        "Busy indicator types",
        ["spinners", "pulse"],
        multiple=True,
        selected=["spinners", "pulse"],
    )

    @render.download
    def download():
        time.sleep(3)
        path = os.path.join(os.path.dirname(__file__), "app-express.py")
        return path


with ui.card():
    ui.card_header(
        "Plot that takes a few seconds to render",
        ui.input_task_button("simulate", "Simulate"),
        class_="d-flex justify-content-between align-items-center",
    )

    @render.plot
    def plot():
        input.simulate()
        time.sleep(3)
        sns.lineplot(x=np.arange(100), y=np.random.randn(100))


ui.busy_indicators.options(spinner_type="bars3")


@render.ui
def indicator_types_ui():
    return ui.busy_indicators.use(
        spinners="spinners" in input.indicator_types(),
        pulse="pulse" in input.indicator_types(),
    )
