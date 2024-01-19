from conftest import ShinyAppProc
from controls import OutputTextVerbatim
from playwright.sync_api import Page
from playwright.sync_api import expect as playwright_expect


def test_express_page_fluid(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    txt = OutputTextVerbatim(page, "visible")
    txt.expect_value("40")

    playwright_expect(page.locator("#visible")).to_have_count(1)
    playwright_expect(page.locator("#hidden")).to_have_count(0)
