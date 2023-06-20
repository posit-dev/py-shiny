import matplotlib.pyplot as plt
import numpy as np

from shiny import App, Inputs, Outputs, Session
from shiny import experimental as x
from shiny import render, ui

app_ui = ui.page_fixed(
    x.ui.layout_sidebar(
        ui.output_plot("plot"),
        sidebar=x.ui.sidebar(ui.input_slider("n", "N", min=0, max=100, value=20)),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.plot(alt="A histogram")
    def plot() -> object:
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.n(), density=True)
        return fig


app = App(app_ui, server)
