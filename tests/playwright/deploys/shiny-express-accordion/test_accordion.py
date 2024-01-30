from controls import Accordion
from playwright.sync_api import Page
from utils.deploy_utils import create_deploys_app_url_fixture, skip_if_not_chrome

app_url = create_deploys_app_url_fixture("shiny_express_accordion")


@skip_if_not_chrome
def test_express_accordion(page: Page, app_url: str) -> None:
    page.goto(app_url)

    acc = Accordion(page, "express_accordion")
    acc_panel_2 = acc.accordion_panel("Panel 2")
    acc_panel_2.expect_open(True)
    acc_panel_2.expect_body("n = 50")
    acc_panel_2.set(False)
    acc_panel_2.expect_open(False)
