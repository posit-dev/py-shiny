import matplotlib.pyplot as plt
import numpy as np

from shiny import render
from shiny.express import input, ui

with ui.accordion(open=["Panel 1", "Panel 2"]):
    with ui.accordion_panel("Panel 1"):
        ui.input_slider("n", "N", 1, 100, 50)

    with ui.accordion_panel("Panel 2"):

        @render.text
        def txt():
            return f"n = {input.n()}"


@render.plot
def histogram():
    x = 100 + 15 * np.random.default_rng(seed=19680801).standard_normal(437)
    plt.hist(x, input.n(), density=True)
