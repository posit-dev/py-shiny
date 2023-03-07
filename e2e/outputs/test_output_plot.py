import re

from conftest import ShinyAppProc, create_doc_example_fixture
from controls import OutputPlot
from playwright.sync_api import Page

app = create_doc_example_fixture("output_plot")


def test_output_plot_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    plot = OutputPlot(page, "p")

    plot.expect_inline(inline=False)
    plot.expect_height("400px")
    plot.expect_width("100%")

    plot.expect_img_src(re.compile(r"data:image/png;base64"))
    plot.expect_img_height("100%")
    plot.expect_img_width("100%")
    plot.expect_img_alt(None)
