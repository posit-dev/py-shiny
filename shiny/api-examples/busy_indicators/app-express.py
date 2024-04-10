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


ui.input_selectize(
    "indicator_types",
    "Busy indicator types",
    ["spinners", "pulse", "cursor"],
    multiple=True,
    selected=["spinners", "pulse"],
)


@render.express
def indicator_types_ui():
    ui.busy_indicators.use(input.indicator_types())
