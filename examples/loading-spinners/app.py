# pyright:basic
import time

import matplotlib.pyplot as mpl
import numpy as np
import seaborn as sns
from faicons import icon_svg

from shiny import App, module, reactive, render, ui


# -- Reusable card module --
@module.ui
def card_ui(title="Tadpole", spinner_type="tadpole"):
    return ui.card(
        ui.card_header(
            title,
            ui.input_task_button("simulate", "Simulate", icon=icon_svg("shuffle")),
            class_="d-flex justify-content-between align-items-center",
        ),
        ui.loading_indicators.spinner_options(
            spinner_type, css_selector="." + spinner_type
        ),
        ui.output_plot("plot"),
        class_=spinner_type,
    )


@module.server
def card_server(input, output, session, length, simulate_all):

    @ui.bind_task_button(button_id="simulate")
    @reactive.extended_task
    async def plot_task(initial, length):
        time.sleep(0.5 if initial else length)

        # Without ax, seaborn works through side effects, so supply the ax to avoid
        # one figure from affecting another.
        fig, ax = mpl.subplots(1, 1)
        sns.lineplot(x=np.arange(100), y=np.random.randn(100), ax=ax)
        return fig

    @reactive.effect
    @reactive.event(input.simulate, ignore_none=False)
    def _():
        plot_task(initial=input.simulate() == 0, length=length())

    @reactive.effect
    @reactive.event(simulate_all)
    def _():
        simulate_all()
        plot_task(initial=False, length=length())

    @render.plot
    def plot():
        return plot_task.result()


# -- Main app --
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_task_button("simulate_all", "Simulate all", icon=icon_svg("shuffle")),
        ui.input_select("loading_mode", "Loading mode", ["spinners", "cursor", "none"]),
        ui.input_slider("length", "Simulation length", 0, 1000, 3),
    ),
    ui.layout_columns(
        card_ui("a", "Tadpole", "tadpole"),
        card_ui("b", "Disc", "disc"),
        card_ui("c", "Dots", "dots"),
        card_ui("d", "Dot track", "dot-track"),
        col_widths=[6, 6],
    ),
    card_ui("e", "Ball", "bounce"),
    ui.output_ui("loading_mode_ui"),
    ui.output_ui("some_text"),
    fillable=True,
)


def server(input, output, session):

    @render.ui
    def loading_mode_ui():
        return ui.loading_indicators.mode(input.loading_mode())

    card_server("a", length=input.length, simulate_all=input.simulate_all)
    card_server("b", length=input.length, simulate_all=input.simulate_all)
    card_server("c", length=input.length, simulate_all=input.simulate_all)
    card_server("d", length=input.length, simulate_all=input.simulate_all)
    card_server("e", length=input.length, simulate_all=input.simulate_all)

    # @render.ui
    # def some_text():
    #    input.simulate_all()
    #    time.sleep(input.length())
    #    return ui.markdown(
    #        "This app demonstrates the use of different loading spinners."
    #    )


app = App(app_ui, server)
