from conftest import ShinyAppProc
from controls import Accordion
from playwright.sync_api import Page


def test_express_accordion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    acc = Accordion(page, "express_accordion")
    acc_panel_2 = acc.accordion_panel("Panel 2")
    acc_panel_2.expect_open(True)
    acc_panel_2.expect_body("a = 50")
    acc_panel_2.set(False)
    acc_panel_2.expect_open(False)
