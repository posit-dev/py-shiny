import asyncio

import matplotlib.pyplot as plt
import numpy as np

from shiny import App, reactive, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("rows", "Rows", 0, 100, 20),
    ),
    ui.use_loading_spinners(page_level=False),
    ui.layout_column_wrap(
        ui.card(
            ui.output_plot("plot"),
        ),
        ui.card(
            ui.output_plot("plot2"),
            # ui.div({"class": "recalculating"}, style="height: 200px; width: 100%;"),
        ),
    ),
)


def server(input, output, session):
    first_render = reactive.value(True)

    @render.plot
    async def plot():
        # Generate input.rows() random numbers
        data = np.random.randn(input.rows())
        plt.plot(data)
        plt.ylabel("some numbers")

        # Only sleep on subsequent renders so we can quickly start looking at the
        # spinner
        with reactive.isolate():
            if not first_render.get():
                # Sleep for a second to simulate a long running process
                await asyncio.sleep(3)
            else:
                first_render.set(False)

        return plt.gcf()

    @render.plot
    async def plot2():
        # Generate input.rows() random numbers
        data = np.random.randn(input.rows())
        plt.plot(data)
        plt.ylabel("some numbers")
        # Sleep for a second to simulate a long running process

        return plt.gcf()


app = App(app_ui, server)
