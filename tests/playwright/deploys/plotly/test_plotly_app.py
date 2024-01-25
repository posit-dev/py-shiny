import os

import pytest
from playwright.sync_api import Page, expect
from utils.deploy_utils import (
    deploy_locations,
    prepare_deploy_and_open_url,
    skip_if_not_python_310,
)

COUNTRY = "Afghanistan"
APP_NAME = "example_deploy_app_A"
app_file_path = os.path.dirname(os.path.abspath(__file__))
EXPECT_TIMEOUT = 120 * 1000


@skip_if_not_python_310
@pytest.mark.only_browser("chromium")
@pytest.mark.parametrize("location", deploy_locations)
def test_deploys(page: Page, location: str) -> None:
    prepare_deploy_and_open_url(page, app_file_path, location, APP_NAME)

    expect(page.get_by_text(COUNTRY)).to_have_count(1, timeout=EXPECT_TIMEOUT)
    page.get_by_role("cell", name=COUNTRY).click(timeout=EXPECT_TIMEOUT)
    expect(page.locator("#country_detail_pop")).to_contain_text(
        COUNTRY, timeout=EXPECT_TIMEOUT
    )
    expect(page.locator("#country_detail_percap")).to_contain_text(
        COUNTRY, timeout=EXPECT_TIMEOUT
    )
    expect(page.get_by_text(COUNTRY)).to_have_count(3, timeout=EXPECT_TIMEOUT)
