# pyright:basic
import time

import numpy as np
import seaborn as sns
from faicons import icon_svg

from shiny import App, module, reactive, render, ui


# -- Reusable card module --
@module.ui
def card_ui(spinner_type):
    return ui.card(
        ui.busy_indicators.options(spinner_type=spinner_type),
        ui.card_header("Spinner:" + spinner_type),
        ui.output_plot("plot"),
    )


@module.server
def card_server(input, output, session, simulate):

    @render.plot
    def plot():
        time.sleep(1)
        if simulate() > 0:
            time.sleep(100)
        sns.lineplot(x=np.arange(100), y=np.random.randn(100))


# -- Main app --
app_ui = ui.page_fillable(
    ui.input_task_button("simulate", "Simulate"),
    ui.layout_columns(
        card_ui("ring", "ring"),
        card_ui("bars", "bars"),
        card_ui("dots", "dots"),
        card_ui("pulse", "pulse"),
        col_widths=6,
    ),
)


def server(input, output, session):

    @reactive.calc
    def simulate():
        return input.simulate()

    card_server("ring", simulate=simulate)
    card_server("bars", simulate=simulate)
    card_server("dots", simulate=simulate)
    card_server("pulse", simulate=simulate)


app = App(app_ui, server)
