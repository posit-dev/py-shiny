import matplotlib.pyplot as plt
import numpy as np

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("obs", "Number of bins:", min=10, max=100, value=30),
    ui.output_plot("distPlot"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.plot
    def distPlot():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.obs(), density=True)
        return fig


app = App(app_ui, server)
