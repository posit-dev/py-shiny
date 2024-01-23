import os

import pytest
from conftest import ShinyAppProc
from controls import Accordion
from playwright.sync_api import Page
from utils.deploy_utils import prepare_deploy_and_open_url

APP_NAME = "shiny_express_accordion"
app_file_path = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.only_browser("chromium")
@pytest.mark.parametrize("location", ["connect", "shinyapps", "local"])
def test_express_accordion(page: Page, location: str, local_app: ShinyAppProc) -> None:
    if location == "local":
        page.goto(local_app.url)
    else:
        prepare_deploy_and_open_url(page, app_file_path, location, APP_NAME)
    acc = Accordion(page, "express_accordion")
    acc_panel_2 = acc.accordion_panel("Panel 2")
    acc_panel_2.expect_open(True)
    acc_panel_2.expect_body("n = 50")
    acc_panel_2.set(False)
    acc_panel_2.expect_open(False)
