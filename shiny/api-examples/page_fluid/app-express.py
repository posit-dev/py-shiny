import matplotlib.pyplot as plt
import numpy as np

from shiny.express import input, render, ui

# Equivalent to using `ui.page_fluid()` in the core API
ui.page_opts(full_width=True)

with ui.layout_sidebar():
    with ui.sidebar():
        ui.input_slider("n", "N", min=0, max=100, value=20)

    @render.plot(alt="A histogram")
    def plot() -> object:
        x = 100 + 15 * np.random.default_rng(seed=19680801).randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.n(), density=True)
        return fig
