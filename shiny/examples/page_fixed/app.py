import matplotlib.pyplot as plt
import numpy as np

from shiny import *
from shiny import experimental as x

app_ui = ui.page_fixed(
    x.ui.layout_sidebar(
        x.ui.panel_sidebar(ui.input_slider("n", "N", min=0, max=100, value=20)),
        x.ui.panel_main(ui.output_plot("plot")),
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
