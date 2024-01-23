import os

import pytest
from conftest import ShinyAppProc
from playwright.sync_api import Page
from utils.deploy_utils import prepare_deploy_and_open_url
from controls import LayoutNavsetTab

APP_NAME = "shiny-express-folium"
app_file_path = os.path.dirname(os.path.abspath(__file__))

@pytest.mark.only_browser("chromium")
@pytest.mark.parametrize("location", ["connect", "shinyapps", "local"])
def test_page_default(page: Page, location: str, local_app: ShinyAppProc) -> None:
    if location == "local":
        page.goto(local_app.url)
    else:
        prepare_deploy_and_open_url(page, app_file_path, location, APP_NAME)
    nav_html = LayoutNavsetTab(page, "express_navset_tab")
    nav_html.expect_content("pre 0pre 1pre 2")
    nav_html.set("div")
    nav_html.expect_content("div 0\ndiv 1\ndiv 2")
    nav_html.set("span")
    nav_html.expect_content("span 0span 1span 2")
    navset_card_tab = LayoutNavsetTab(page, "express_navset_card_tab")
    navset_card_tab.expect_content("")
    # since it is a custom table we can't use the OutputTable controls
    shell_text = page.locator("#shell").inner_text().strip()
    assert shell_text == (
        "R1C1R1\nR1C1R2-R1C1R1\nR1C1R2-R1C1R2\nR1C1R2-R1C2\nR1C2"
    ), "Locator contents don't match expected text"
