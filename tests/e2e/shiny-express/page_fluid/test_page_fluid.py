from conftest import ShinyAppProc
from controls import OutputPlot
from playwright.sync_api import Page


def test_express_page_fluid(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    plot = OutputPlot(page, "histogram")
    plot.expect_img_height("100%")
    plot.expect_img_width("100%")
