import matplotlib.pyplot as plt
import numpy as np

from shiny.express import input, render, ui

ui.input_slider("n", "input_slider()", min=10, max=100, value=50, step=5, animate=True)


@render.plot
def p():
    x_rand = 100 + 15 * np.random.default_rng(seed=19680801).randn(437)
    fig, ax = plt.subplots()
    ax.hist(x_rand, int(input.n()), density=True)
    return fig
