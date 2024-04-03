# pyright:basic
import time

import matplotlib.pyplot as plt
import numpy as np

from shiny import App, module, render, ui


# -- Reusable card module --
@module.ui
def card_ui():
    return ui.card(
        ui.card_header(
            "A plot",
            ui.input_action_button("update", "Update"),
        ),
        ui.output_plot("plot"),
    )


@module.server
def card_server(input, output, session, length):

    def draw_plot():
        data = np.random.randn(100)
        plt.plot(data)
        plt.ylabel("some numbers")
        return plt.gcf()

    @render.plot
    def plot():
        if input.update() > 0:
            time.sleep(length())
        else:
            time.sleep(4)
        return draw_plot()


# -- Main app --
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("length", "Sleep length", 0, 1000, 40),
    ),
    ui.loading_spinners(color="red"),
    ui.layout_columns(
        card_ui("a"), card_ui("b"), card_ui("c"), card_ui("d"), col_widths=[6, 6]
    ),
    fillable=True,
)


def server(input, output, session):

    card_server("a", length=input.length)
    card_server("b", length=input.length)
    card_server("c", length=input.length)
    card_server("d", length=input.length)


app = App(app_ui, server)
