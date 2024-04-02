import matplotlib.pyplot as plt
import numpy as np

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_navbar(
    ui.nav_panel(
        "One",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_slider("n", "N", min=0, max=100, value=20),
            ),
            ui.output_plot("plot"),
        ),
    ),
    ui.nav_panel(
        "Two",
        ui.layout_column_wrap(
            ui.card("Second page content."),
            ui.card(
                ui.card_header("Server-side color mode setting"),
                ui.input_action_button("make_light", "Switch to light mode"),
                ui.input_action_button("make_dark", "Switch to dark mode"),
            ),
        ),
    ),
    ui.nav_spacer(),
    ui.nav_control(ui.input_dark_mode(id="mode")),
    title="Shiny Dark Mode",
    id="page",
    fillable="One",
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.make_light)
    def _():
        ui.update_dark_mode("light")

    @reactive.effect
    @reactive.event(input.make_dark)
    def _():
        ui.update_dark_mode("dark")

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


app = App(app_ui, server)
