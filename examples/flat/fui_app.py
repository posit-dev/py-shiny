import matplotlib.pyplot as plt
import numpy as np

from shiny import render, ui
from shiny.flat import input
from shiny.flat import ui as uic

with uic.page_sidebar():
    with uic.sidebar():
        ui.input_slider("n", "N", 1, 100, 50)

    @render.plot
    def histogram():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)
        plt.hist(x, input.n(), density=True)
