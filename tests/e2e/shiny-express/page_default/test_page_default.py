from conftest import ShinyAppProc
from controls import LayoutNavsetTab
from playwright.sync_api import Page


def test_express_accordion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    nav_html = LayoutNavsetTab(page, "express_navset_tab")
    nav_html.expect_content("pre 0pre 1pre 2")
    nav_html.set("div")
    nav_html.expect_content("div 0\ndiv 1\ndiv 2")
    nav_html.set("span")
    nav_html.expect_content("span 0span 1span 2")
    navset_card_tab = LayoutNavsetTab(page, "express_navset_card_tab")
    navset_card_tab.expect_content("Ellipsis")
    # since it is a custom table we can't use the OutputTable controls
    shell = page.locator("#shell")
    # Ask-Barret: /n affecting one browser but not the other
    assert shell.inner_text() == (
        "'R1C1R1'\n'R1C1R2-R1C1R1'\n'R1C1R2-R1C1R2'\n'R1C1R2-R1C2'\n'R1C2'\n"
    ), "Locator contents don't match expected text"
