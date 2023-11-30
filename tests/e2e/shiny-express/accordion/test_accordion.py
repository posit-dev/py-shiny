from conftest import ShinyAppProc
from controls import Accordion, LayoutNavsetTab
from playwright.sync_api import Page


def test_express_accordion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    acc = Accordion(page, "express_accordion")
    acc_panel_2 = acc.accordion_panel("Panel 2")
    acc_panel_2.expect_open(True)
    acc_panel_2.expect_body("a = 50")
    nav_html = LayoutNavsetTab(page, "express_navset_tab")
    nav_html.expect_content("pre 0pre 1pre 2")
    nav_html.set("div")
    nav_html.expect_content("div 0\ndiv 1\ndiv 2")
    nav_html.set("span")
    nav_html.expect_content("span 0span 1span 2")
    navset_card_tab = LayoutNavsetTab(page, "express_navset_card_tab")
    navset_card_tab.expect_content("Ellipsis")
    # how to test rows and columns? 😕

