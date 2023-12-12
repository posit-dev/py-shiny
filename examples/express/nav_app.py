import matplotlib.pyplot as plt
import numpy as np

from shiny import render
from shiny.express import input, ui

with ui.layout_column_wrap(width=1 / 2):
    with ui.navset():
        with ui.nav(title="One"):
            ui.input_slider("n", "N", 1, 100, 50)

        with ui.nav(title="Two"):

            @render.plot
            def histogram():
                np.random.seed(19680801)
                x = 100 + 15 * np.random.randn(437)
                plt.hist(x, input.n(), density=True)

    with ui.navset_card():
        with ui.nav(title="One"):
            ui.input_slider("n2", "N", 1, 100, 50)

        with ui.nav(title="Two"):

            @render.plot
            def histogram2():
                np.random.seed(19680801)
                x = 100 + 15 * np.random.randn(437)
                plt.hist(x, input.n2(), density=True)
