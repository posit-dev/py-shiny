from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_express_page_fluid(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    txt = controller.OutputTextVerbatim(page, "visible")
    txt.expect_value("40")

    expect(page.locator("#visible")).to_have_count(1)
    expect(page.locator("#hidden")).to_have_count(0)
