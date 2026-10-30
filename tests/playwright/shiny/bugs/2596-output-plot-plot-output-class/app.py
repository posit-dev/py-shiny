"""
Regression app for #2596.

`controller.OutputPlot` located its element with both `.shiny-image-output` and
`.shiny-plot-output`. `ui.output_plot()` writes both classes, but Shiny for R's
`plotOutput()` writes only `shiny-plot-output`, so the controller found nothing
for an R plot. This app renders the same plot into a regular `ui.output_plot()`
and into an output element that has only the `shiny-plot-output` class.
"""

import matplotlib.pyplot as plt

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.output_plot("py_plot"),
    ui.div(id="plot_only", class_="shiny-plot-output", style="height: 400px;"),
)


def server(input: Inputs, output: Outputs, session: Session):
    def draw():
        fig, ax = plt.subplots()  # pyright: ignore[reportUnknownMemberType]
        ax.plot([1, 2, 3], [1, 4, 9])  # pyright: ignore[reportUnknownMemberType]
        return fig

    @render.plot
    def py_plot():
        return draw()

    @render.plot
    def plot_only():
        return draw()


app = App(app_ui, server)
