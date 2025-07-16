# This app demonstrates how to use "global" variables that are shared across sessions.
# This is useful if you want to load data just once and use it in multiple apps, or if
# you want to share data or reactives among apps.

import matplotlib.pyplot as plt
import numpy as np
import shared

from shiny import reactive, render
from shiny.express import input, ui


@render.plot
def histogram():
    np.random.seed(19680801)
    x = 100 + 15 * np.random.randn(437)
    plt.hist(x, shared.rv(), density=True)


ui.input_slider("n", "N", 1, 100, 50)


@reactive.effect
def _():
    shared.rv.set(input.n())


@render.code
def rv_value():
    return f"shared.rv() = {shared.rv()}"


@render.code
def text_data():
    return "shared.data = " + str(shared.data)


# If another session changes the slider, make sure the slider also reflects that change.
@reactive.effect
def _():
    ui.update_slider("n", value=shared.rv())
