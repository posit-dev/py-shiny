# pyright:basic
import asyncio
import concurrent.futures
import time

import matplotlib.pyplot as mpl
import numpy as np
import seaborn as sns
from faicons import icon_svg

from shiny import App, module, reactive, render, ui

# Execute each extended task on a different thread.
pool = concurrent.futures.ThreadPoolExecutor()

# Use Agg backend for matplotlib so that it doesn't try to open a window.
mpl.switch_backend("Agg")


# -- Reusable card module --
@module.ui
def card_ui(title="Tadpole", spinner_type="tadpole"):
    return ui.card(
        ui.card_header(
            title,
            ui.input_task_button("simulate", "Simulate", icon=icon_svg("shuffle")),
            class_="d-flex justify-content-between align-items-center",
        ),
        ui.busy_indicators.spinner_options(
            spinner_type, css_selector="." + spinner_type
        ),
        ui.output_plot("plot"),
        class_=spinner_type,
    )


@module.server
def card_server(input, output, session, length, simulate_all):

    def do_plot(wait_time=0.5):
        time.sleep(wait_time)

        # Without ax, seaborn works through side effects, so supply the ax to avoid
        # one figure from affecting another.
        fig, ax = mpl.subplots(1, 1)
        sns.lineplot(x=np.arange(100), y=np.random.randn(100), ax=ax)
        return fig

    @ui.bind_task_button(button_id="simulate")
    @reactive.extended_task
    async def plot_task(wait_time=1):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(pool, do_plot, wait_time)

    @reactive.effect
    @reactive.event(input.simulate, ignore_none=False)
    def _():
        plot_task(1 if input.simulate() == 0 else length())

    @reactive.effect
    @reactive.event(simulate_all)
    def _():
        plot_task(length())

    @render.plot
    def plot():
        return plot_task.result()


# -- Main app --
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_task_button("simulate_all", "Simulate all", icon=icon_svg("shuffle")),
        ui.input_selectize(
            "indicator_types",
            "Busy indicator types",
            ["spinners", "pulse"],
            multiple=True,
            selected=["spinners", "pulse"],
        ),
        ui.input_slider("length", "Simulation length", 0, 500, 5),
    ),
    ui.layout_columns(
        card_ui("a", "Tadpole", "tadpole"),
        card_ui("b", "Disc", "disc"),
        card_ui("c", "Dots", "dots"),
        card_ui("d", "Dot track", "dot-track"),
        col_widths=[6, 6],
    ),
    card_ui("e", "Ball", "bounce"),
    ui.output_ui("indicator_types_ui"),
    fillable=True,
    title="Busy indicators + extended tasks = ❤️",
)


def server(input, output, session):

    @render.ui
    def indicator_types_ui():
        return ui.busy_indicators.use(input.indicator_types())

    card_server("a", length=input.length, simulate_all=input.simulate_all)
    card_server("b", length=input.length, simulate_all=input.simulate_all)
    card_server("c", length=input.length, simulate_all=input.simulate_all)
    card_server("d", length=input.length, simulate_all=input.simulate_all)
    card_server("e", length=input.length, simulate_all=input.simulate_all)


app = App(app_ui, server)
app.on_shutdown(pool.shutdown)
