# pyright:basic
import time

import numpy as np
import seaborn as sns

from shiny import App, module, reactive, render, ui


# -- Reusable card module --
@module.ui
def card_ui(spinner_type):
    return ui.card(
        ui.busy_indicators.options(spinner_type=spinner_type),
        ui.card_header("Spinner: " + spinner_type),
        ui.output_plot("plot"),
    )


@module.server
def card_server(input, output, session, rerender):
    @render.plot
    def plot():
        rerender()
        time.sleep(1)
        sns.lineplot(x=np.arange(100), y=np.random.randn(100))


# -- Main app --
app_ui = ui.page_fillable(
    ui.input_task_button("rerender", "Re-render"),
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
    def rerender():
        return input.rerender()

    card_server("ring", rerender=rerender)
    card_server("bars", rerender=rerender)
    card_server("dots", rerender=rerender)
    card_server("pulse", rerender=rerender)


app = App(app_ui, server)
