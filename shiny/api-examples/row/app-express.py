import matplotlib.pyplot as plt
import numpy as np

from shiny.express import input, render, ui

with ui.row():
    with ui.column(4):
        ui.input_slider("n", "N", min=1, max=100, value=20)

    with ui.column(8):

        @render.plot(alt="A histogram")
        def plot():
            np.random.seed(19680801)
            x = 100 + 15 * np.random.randn(437)

            fig, ax = plt.subplots()
            ax.hist(x, input.n(), density=True)
            return fig
