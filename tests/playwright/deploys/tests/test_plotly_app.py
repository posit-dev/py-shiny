import os

import pytest
from playwright.sync_api import Page, expect
from utils.deploy_utils import deploy, write_requirements_txt

COUNTRY = "Afghanistan"
APP_DIR = "plotly_app"
APP_NAME = "example_deploy_app_A"
# reqd since the app on connect takes a while to load
PAGE_TIMEOUT = 120 * 1000
EXPECT_TIMEOUT = 30 * 1000


current_dir = os.path.dirname(os.path.abspath(__file__))
app_file_path = os.path.join(os.path.dirname(current_dir), "apps", APP_DIR)


@pytest.mark.integrationtest
@pytest.mark.only_browser("chromium")
@pytest.mark.parametrize("location", ["connect", "shinyapps"])
def test_deploys(page: Page, location: str) -> None:
    write_requirements_txt(app_file_path)
    page_url = deploy(location, APP_NAME, app_file_path)
    page.goto(page_url, timeout=PAGE_TIMEOUT)

    expect(page.get_by_text(COUNTRY)).to_have_count(1, timeout=EXPECT_TIMEOUT)
    page.get_by_role("cell", name=COUNTRY).click(timeout=EXPECT_TIMEOUT)
    expect(page.locator("#country_detail_pop")).to_contain_text(
        COUNTRY, timeout=EXPECT_TIMEOUT
    )
    expect(page.locator("#country_detail_percap")).to_contain_text(
        COUNTRY, timeout=EXPECT_TIMEOUT
    )
    expect(page.get_by_text(COUNTRY)).to_have_count(3, timeout=EXPECT_TIMEOUT)
