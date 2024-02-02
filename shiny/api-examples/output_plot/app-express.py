import matplotlib.pyplot as plt
import numpy as np

from shiny.express import input, render, ui

ui.input_slider("n", "input_slider()", min=10, max=100, value=50, step=5, animate=True)


@render.plot
def p():
    np.random.seed(19680801)
    x_rand = 100 + 15 * np.random.randn(437)
    fig, ax = plt.subplots()
    ax.hist(x_rand, int(input.n()), density=True)
    return fig
