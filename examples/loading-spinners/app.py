# pyright:basic
import time

import matplotlib.pyplot as mpl
import numpy as np
import seaborn as sns

from shiny import App, module, reactive, render, ui


# -- Reusable card module --
@module.ui
def card_ui(title="Tadpole", spinner_type="tadpole"):
    return ui.card(
        ui.card_header(
            title,
            ui.input_task_button("update", "Update"),
            class_="d-flex justify-content-between align-items-center",
        ),
        ui.loading_spinners.settings(spinner_type, css_selector="." + spinner_type),
        ui.output_plot("plot"),
        class_=spinner_type,
    )


@module.server
def card_server(input, output, session, length, update_all):

    @ui.bind_task_button(button_id="update")
    @reactive.extended_task
    async def plot_task(initial, length):
        time.sleep(0.5 if initial else length)

        # Without ax, seaborn works through side effects, so supply the ax to avoid
        # one figure from affecting another.
        fig, ax = mpl.subplots(1, 1)
        sns.lineplot(x=np.arange(100), y=np.random.randn(100), ax=ax)
        return fig

    @reactive.effect
    @reactive.event(input.update, ignore_none=False)
    def _():
        plot_task(initial=input.update() == 0, length=length())

    @reactive.effect
    @reactive.event(update_all)
    def _():
        update_all()
        plot_task(initial=False, length=length())

    @render.plot
    def plot():
        return plot_task.result()


# -- Main app --
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("length", "Update length", 0, 1000, 3),
        ui.input_task_button("update_all", "Update all"),
        ui.input_switch("disable", "Disable spinners", False),
    ),
    ui.layout_columns(
        card_ui("a", "Tadpole", "tadpole"),
        card_ui("b", "Disc", "disc"),
        card_ui("c", "Dots", "dots"),
        card_ui("d", "Dot track", "dot-track"),
        col_widths=[6, 6],
    ),
    card_ui("e", "Ball", "bounce"),
    ui.output_ui("disable_spinners"),
    fillable=True,
)


def server(input, output, session):

    @render.ui
    def disable_spinners():
        if input.disable():
            return ui.loading_spinners.disable()
        else:
            return ui.loading_spinners.enable()

    card_server("a", length=input.length, update_all=input.update_all)
    card_server("b", length=input.length, update_all=input.update_all)
    card_server("c", length=input.length, update_all=input.update_all)
    card_server("d", length=input.length, update_all=input.update_all)
    card_server("e", length=input.length, update_all=input.update_all)


app = App(app_ui, server)
