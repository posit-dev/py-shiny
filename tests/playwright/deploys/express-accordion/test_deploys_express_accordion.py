import pytest
from playwright.sync_api import Page
from utils.deploy_utils import (
    local_deploys_app_url_fixture,
    reruns,
    reruns_delay,
    skip_if_not_chrome,
)

from shiny.playwright import controller

app_url = local_deploys_app_url_fixture("shiny_express_accordion")


@skip_if_not_chrome
@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
def test_express_accordion(page: Page, app_url: str) -> None:
    page.goto(app_url)

    acc = controller.Accordion(page, "express_accordion")
    acc_panel_2 = acc.accordion_panel("Panel 2")
    acc_panel_2.expect_open(True)
    acc_panel_2.expect_body("n = 50")
    acc_panel_2.set(False)
    acc_panel_2.expect_open(False)
