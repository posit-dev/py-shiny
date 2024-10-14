import re

from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("output_plot")


def test_output_plot_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    plot = controller.OutputPlot(page, "p")

    plot.expect_inline(False)
    plot.expect_height("400px")
    plot.expect_width("100%")

    plot.expect_img_src(re.compile(r"data:image/png;base64"))
    plot.expect_img_height("100%")
    plot.expect_img_width("100%")
    plot.expect_img_alt(None)
