# pyright:basic
import time

import matplotlib.pyplot as mpl
import numpy as np
import seaborn as sns

from shiny import App, reactive, render, ui

# -- Main app --
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_task_button("update", "Update"),
        ui.input_slider("length", "Update length", 0, 1000, 1),
    ),
    ui.output_ui("foo"),
    fillable=True,
)


def server(input, output, session):

    time.sleep(2)

    @reactive.calc
    def wait_time():
        return input.length() if input.update() > 0 else 0.5

    @render.ui
    def foo():
        time.sleep(wait_time())
        return [ui.output_ui("short"), ui.output_ui("long"), ui.output_plot("p")]

    @render.ui
    def short():
        time.sleep(wait_time())

        return ui.markdown(
            "This app demonstrates the use of different loading spinners."
        )

    @render.ui
    def long():
        time.sleep(wait_time())

        return ui.markdown(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        )

    @render.plot
    def p():
        time.sleep(wait_time())

        mpl.clf()
        sns.histplot(np.random.randn(1000), kde=True)
        return mpl.gcf()


app = App(app_ui, server)
