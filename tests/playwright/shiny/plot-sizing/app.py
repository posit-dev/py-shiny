from __future__ import annotations

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from PIL import Image
from plotnine import aes, element_rect, geom_point, theme, theme_minimal
from plotnine.data import mtcars
from plotnine.ggplot import ggplot

from shiny import App, Inputs, Outputs, Session, module, render, req, ui

tips = sns.load_dataset("tips")
dpi = 150


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

    @render.plot(width=0, height=0)
    def plot_native_size():
        return plot_fn((300, 200))


app_ui = ui.page_navbar(
    ui.nav_panel(
        "matplotlib",
        ui.p(
            "The following four plots should all be the same size. The last one should have larger text."
        ),
        plot_ui("mpl"),
        value="mpl",
    ),
    ui.nav_panel(
        "seaborn",
        ui.p(
            "The following four plots should all be the same size. The last one should have larger text."
        ),
        plot_ui("sns"),
        value="sns",
    ),
    ui.nav_panel(
        "plotnine",
        ui.p(
            "The following four plots should all be the same size. The last one should have larger text."
        ),
        plot_ui("plotnine"),
    ),
    ui.nav_panel(
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

    def plot_with_sns(fig_size: tuple[float, float] | None) -> object:
        kwargs = dict()
        if fig_size:
            kwargs["height"] = fig_size[1] / dpi
            kwargs["aspect"] = fig_size[0] / fig_size[1]

        # FacetGrid has an opinion about its figure size
        g = sns.FacetGrid(tips, **kwargs)  # pyright: ignore[reportUnknownArgumentType]
        g.figure.set_facecolor("lavender")
        g.map(
            sns.scatterplot,  # pyright: ignore[reportUnknownArgumentType]
            "total_bill",
            "tip",
        )
        plt.gca().set_facecolor("lavender")
        if fig_size:
            plt.gcf().set_dpi(dpi)

    def plot_with_plotnine(fig_size: tuple[float, float] | None) -> object:
        p = (
            ggplot(mtcars, aes("wt", "mpg"))
            + geom_point()
            + theme_minimal()
            + theme(
                plot_background=element_rect(fill="lavender"),
                legend_background=element_rect(fill="lavender"),
            )
        )
        if fig_size is not None:
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
    plot_server("sns", plot_with_sns)
    plot_server("plotnine", plot_with_plotnine)
    plot_server("pil", plot_with_pil)


app = App(app_ui, server)
