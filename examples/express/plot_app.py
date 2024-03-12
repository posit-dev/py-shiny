import matplotlib.pyplot as plt
import numpy as np

from shiny import render
from shiny.express import input, ui

ui.input_slider("n", "N", 1, 100, 50)


@render.plot
def histogram():
    x = 100 + 15 * np.random.RandomState(seed=19680801).randn(437)
    plt.hist(x, input.n(), density=True)
