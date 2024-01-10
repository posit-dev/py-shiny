from math import ceil

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def hide_ticks(axis):
    for ticks in [axis.get_major_ticks(), axis.get_minor_ticks()]:
        for tick in ticks:
            tick.tick1line.set_visible(False)
            tick.tick2line.set_visible(False)
            tick.label1.set_visible(False)
            tick.label2.set_visible(False)


def plot_cpu(history, nsamples, ncpu, cmap):
    if history is None:
        history = np.array([])
        history.shape = (ncpu, 0)

    # Throw away samples too old to fit on the plot
    if history.shape[1] > nsamples:
        history = history[:, -nsamples:]

    ncols = 2
    nrows = int(ceil(ncpu / ncols))
    fig, axeses = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        squeeze=False,
    )
    for i in range(0, ncols * nrows):
        row = i // ncols
        col = i % ncols
        axes = axeses[row, col]
        if i >= len(history):
            axes.set_visible(False)
            continue
        data = history[i]
        axes.yaxis.set_label_position("right")
        axes.yaxis.tick_right()
        axes.set_xlim(-(nsamples - 1), 0)
        axes.set_ylim(0, 100)

        assert len(data) <= nsamples

        # Set up an array of x-values that will right-align the data relative to the
        # plotting area
        x = np.arange(0, len(data))
        x = np.flip(-x)

        # Color bars by cmap
        color = plt.get_cmap(cmap)(data / 100)
        axes.bar(x, data, color=color, linewidth=0, width=1.0)

        axes.set_yticks([25, 50, 75])
        for ytl in axes.get_yticklabels():
            if col == ncols - 1 or i == ncpu - 1 or True:
                ytl.set_fontsize(7)
            else:
                ytl.set_visible(False)
                hide_ticks(axes.yaxis)
        for xtl in axes.get_xticklabels():
            xtl.set_visible(False)
        hide_ticks(axes.xaxis)
        axes.grid(True, linewidth=0.25)

    return fig
