"""
Regression test for #2596: `controller.OutputPlot` finds plot outputs by
`.shiny-plot-output` alone, so it also works for markup without
`.shiny-image-output`, such as Shiny for R's `plotOutput()`.
"""

import re

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_output_plot_finds_plot_output_class(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    for plot_id in ["py_plot", "plot_only"]:
        plot = controller.OutputPlot(page, plot_id)
        plot.expect_img_src(re.compile(r"^data:image/png;base64"))


def test_output_image_still_needs_image_output_class(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    controller.OutputImage(page, "py_plot").expect_img_src(
        re.compile(r"^data:image/png;base64")
    )
