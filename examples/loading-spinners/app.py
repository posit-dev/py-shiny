import asyncio

import matplotlib.pyplot as plt
import numpy as np

from shiny import App, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("rows", "Rows", 0, 100, 20),
    ),
    ui.use_loading_spinners(),
    ui.layout_column_wrap(
        ui.card(
            ui.output_plot("plot"),
        ),
        ui.card(
            ui.output_plot("plot2"),
        ),
    ),
)


def server(input, output, session):
    @render.plot
    async def plot():
        # Generate input.rows() random numbers
        data = np.random.randn(input.rows())
        plt.plot(data)
        plt.ylabel("some numbers")

        # Sleep for a second to simulate a long running process
        await asyncio.sleep(2)

        return plt.gcf()

    @render.plot
    async def plot2():
        # Generate input.rows() random numbers
        data = np.random.randn(input.rows())
        plt.plot(data)
        plt.ylabel("some numbers")
        # Sleep for a second to simulate a long running process
        await asyncio.sleep(0.1)

        return plt.gcf()


app = App(app_ui, server)
