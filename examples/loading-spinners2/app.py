# pyright:basic
import time

import matplotlib.pyplot as mpl
import numpy as np
import seaborn as sns

from shiny import App, module, reactive, render, ui

# -- Main app --
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_task_button("update", "Update"),
        ui.input_slider("length", "Update length", 0, 1000, 3),
    ),
    ui.output_ui("foo"),
    # ui.output_plot("p"),
    fillable=True,
)


def server(input, output, session):

    @reactive.calc
    def wait_time():
        return input.length() if input.update() > 0 else 0.5

    @render.ui
    def foo():
        return [
            ui.output_ui("some_text"),
            ui.output_plot("p"),
        ]

    @render.ui
    def some_text():
        time.sleep(wait_time())

        return ui.markdown(
            "This app demonstrates the use of different loading spinners."
        )

    @render.plot
    def p():
        time.sleep(wait_time())

        mpl.clf()
        sns.histplot(np.random.randn(1000), kde=True)
        return mpl.gcf()


app = App(app_ui, server)
