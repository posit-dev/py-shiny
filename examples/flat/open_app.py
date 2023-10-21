import matplotlib.pyplot as plt
import numpy as np

from shiny import render, ui
from shiny.flat import input
from shiny.flat import open as oui

with oui.page_sidebar.open():
    with oui.sidebar.open():
        ui.input_slider("n", "N", 1, 100, 50)

    @render.plot
    def histogram():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)
        plt.hist(x, input.n(), density=True)


with oui.page_sidebar2.open():
    with oui.sidebar2.open():
        ui.input_slider("n2", "N", 1, 100, 50)

    @render.plot
    def histogram2():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)
        plt.hist(x, input.n2(), density=True)
