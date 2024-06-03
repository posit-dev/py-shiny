import matplotlib.pyplot as plt
import numpy as np

from shiny import reactive
from shiny.express import input, render, ui

ui.page_opts(title="Shiny Dark Mode", fillable="One")

with ui.nav_panel("One"):
    with ui.layout_sidebar():
        with ui.sidebar():
            ui.input_slider("n", "N", min=0, max=100, value=20)

        @render.plot(alt="A histogram")
        def plot() -> object:
            np.random.seed(19680801)
            x = 100 + 15 * np.random.randn(437)

            fig, ax = plt.subplots()
            ax.hist(x, input.n(), density=True)

            # Theme the plot to match light/dark mode
            fig.patch.set_facecolor("none")
            ax.set_facecolor("none")

            color_fg = "black" if input.mode() == "light" else "silver"
            ax.tick_params(axis="both", colors=color_fg)
            ax.spines["bottom"].set_color(color_fg)
            ax.spines["top"].set_color(color_fg)
            ax.spines["left"].set_color(color_fg)
            ax.spines["right"].set_color(color_fg)

            return fig


with ui.nav_panel("Two"):
    with ui.layout_column_wrap():
        with ui.card():
            "Second page content."

        with ui.card():
            ui.card_header("More content on the second page.")
            ui.input_action_button("make_light", "Switch to light mode")
            ui.input_action_button("make_dark", "Switch to dark mode")

ui.nav_spacer()
with ui.nav_control():
    ui.input_dark_mode(id="mode")


@reactive.effect
@reactive.event(input.make_light)
def _():
    ui.update_dark_mode("light")


@reactive.effect
@reactive.event(input.make_dark)
def _():
    ui.update_dark_mode("dark")
