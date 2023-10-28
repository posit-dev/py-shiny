import matplotlib.pyplot as plt
import numpy as np

from shiny import render, ui
from shiny.express import input, layout

with layout.layout_column_wrap(width=1 / 2):
    with layout.card():
        ui.input_slider("n", "N", 1, 100, 50)

    with layout.card():

        @render.plot
        def histogram():
            np.random.seed(19680801)
            x = 100 + 15 * np.random.randn(437)
            plt.hist(x, input.n(), density=True)

    with layout.card():

        @render.plot
        def histogram2():
            np.random.seed(19680801)
            x = 100 + 15 * np.random.randn(437)
            plt.hist(x, input.n(), density=True, color="red")
