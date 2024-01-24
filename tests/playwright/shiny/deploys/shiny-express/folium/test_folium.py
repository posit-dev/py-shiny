import os

import pytest
from conftest import ShinyAppProc
from playwright.sync_api import Page, expect
from utils.deploy_utils import prepare_deploy_and_open_url, skip_if_not_python_310

APP_NAME = "shiny-express-folium"
app_file_path = os.path.dirname(os.path.abspath(__file__))


@skip_if_not_python_310
@pytest.mark.only_browser("chromium")
@pytest.mark.parametrize("location", ["connect", "shinyapps", "local"])
def test_folium_map(page: Page, location: str, local_app: ShinyAppProc) -> None:
    if location == "local":
        page.goto(local_app.url)
    else:
        prepare_deploy_and_open_url(page, app_file_path, location, APP_NAME)
    expect(page.get_by_text("Static Map")).to_have_count(1)
    expect(page.get_by_text("Map inside of render express call")).to_have_count(1)
    # map inside the @render.express
    expect(
        page.frame_locator("iframe").nth(1).get_by_role("link", name="OpenStreetMap")
    ).to_have_count(1)
    # map outside of the @render.express at the top level
    expect(
        page.frame_locator("iframe")
        .nth(0)
        .get_by_role("link", name="U.S. Geological Survey")
    ).to_have_count(1)
