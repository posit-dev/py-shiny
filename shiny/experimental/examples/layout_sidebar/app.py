from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    x.ui.layout_sidebar(
        ui.output_plot("p"),
        sidebar=ui.input_slider(
            "n", "input_slider()", min=10, max=100, value=50, step=5, animate=True
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.plot
    def p():
        np.random.seed(19680801)
        x_rand = 100 + 15 * np.random.randn(437)
        fig, ax = plt.subplots()
        ax.hist(x_rand, int(input.n()), density=True)
        return fig


app = App(app_ui, server)
