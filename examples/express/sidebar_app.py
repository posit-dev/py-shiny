import matplotlib.pyplot as plt
import numpy as np

from shiny import render
from shiny.express import input, ui

with ui.sidebar():
    ui.input_slider("n", "N", 1, 100, 50)


@render.plot
def histogram():
    x = 100 + 15 * np.random.default_rng(seed=19680801).standard_normal(437)
    plt.hist(x, input.n(), density=True)
