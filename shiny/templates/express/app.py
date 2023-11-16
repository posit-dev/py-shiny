import random

import matplotlib.pyplot as plt

from shiny import render, ui
from shiny.express import input, layout

random.seed(0)
data = [random.gauss(0, 1) for _ in range(10000)]

with layout.sidebar():
    ui.input_slider("num_bins", "Number of Bins", min=1, max=50, value=30)


@render.plot
def plot():
    plt.hist(data, bins=input.num_bins())
