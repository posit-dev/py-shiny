import matplotlib.pyplot as plt
import numpy as np
from shiny import App, render, ui

# Generate some random numbers
data_x = np.random.standard_normal(400)
data_y = np.random.standard_normal(400)

app_ui = ui.page_fluid(
    ui.input_slider("n", "Number of points", min=10, max=400, value=50, step=10),
    ui.output_plot("scatter_plot"),
)


def server(input, output, session):
    @output
    @render.plot
    def scatter_plot():
        return plt.scatter(data_x[: input.n()], data_y[: input.n()])


app = App(app_ui, server)
