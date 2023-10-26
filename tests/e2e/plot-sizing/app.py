from __future__ import annotations

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from plotnine import aes, element_rect, facet_wrap, geom_point, stat_smooth, theme
from plotnine.data import mtcars
from plotnine.ggplot import ggplot

from shiny import App, Inputs, Outputs, Session, module, render, req, ui


@module.ui
def plot_ui():
    plot_outputs = [
        ui.div(
            ui.output_plot("plot_default"),
            style="width: 300px; height: 200px;",
            class_="html-fill-container",
        ),
        ui.output_plot("plot_dom_size", width="300px", height="200px"),
        ui.output_plot("plot_decorator_size", width="auto", height="auto"),
        ui.output_plot("plot_native_size", width="auto", height="auto"),
    ]

    return ui.TagList(
        [ui.div(x, class_="border mb-3") for x in plot_outputs],
    )


@module.server
def plot_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    plot_fn: Callable[[tuple[float, float] | None], object],
):
    @render.plot
    def plot_default():
        return plot_fn(None)

    @render.plot
    def plot_dom_size():
        return plot_fn(None)

    @render.plot(width=300, height=200)
    def plot_decorator_size():
        return plot_fn(None)

    @render.plot
    def plot_native_size():
        return plot_fn((300, 200))


app_ui = ui.page_navbar(
    ui.nav(
        "matplotlib",
        ui.p(
            "The following four plots should all be the same size. The last one should have larger text."
        ),
        plot_ui("mpl"),
        value="mpl",
    ),
    ui.nav(
        "plotnine",
        ui.p(
            "The following four plots should all be the same size. The last one should have larger text."
        ),
        ui.p("It may take a moment for the plots to render."),
        plot_ui("plotnine"),
    ),
    ui.nav(
        "pil",
        ui.p("The following three images should all be the same size."),
        plot_ui("pil"),
    ),
    id="tabset",
)


def server(input: Inputs, output: Outputs, session: Session):
    def plot_with_mpl(fig_size: tuple[float, float] | None) -> object:
        fig, ax = plt.subplots(facecolor="lavender")
        X, Y = np.mgrid[-4:4, -4:4]
        ax.quiver(X, Y)

        # Background color
        ax.set_facecolor("lavender")

        if fig_size is not None:
            fig.set_dpi(150)
            fig.set_size_inches(
                fig_size[0] / fig.get_dpi(), fig_size[1] / fig.get_dpi()
            )

        return fig

    def plot_with_plotnine(fig_size: tuple[float, float] | None) -> object:
        p = (
            ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
            + geom_point()
            + stat_smooth(method="lm")
            + facet_wrap("~gear")
            + theme(
                plot_background=element_rect(fill="lavender"),
                legend_background=element_rect(fill="lavender"),
            )
        )
        if fig_size is not None:
            dpi = 150
            p = p + theme(
                figure_size=(fig_size[0] / dpi, fig_size[1] / dpi),
                plot_background=element_rect(fill="lavender"),
                dpi=dpi,
            )
        return p

    def plot_with_pil(fig_size: tuple[float, float] | None) -> object:
        req(fig_size is None)
        return Image.open(Path(__file__).parent / "bike.jpg")

    plot_server("mpl", plot_with_mpl)
    plot_server("plotnine", plot_with_plotnine)
    plot_server("pil", plot_with_pil)


app = App(app_ui, server)
