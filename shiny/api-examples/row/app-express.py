import matplotlib.pyplot as plt
import numpy as np

from shiny.express import input, render, ui
from shiny.ui import column, row

with ui.hold() as hist_plot:

    @render.plot(alt="A histogram")
    def plot():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.n(), density=True)
        return fig


row(
    column(4, ui.input_slider("n", "N", min=1, max=100, value=20)),
    column(8, hist_plot),
)
