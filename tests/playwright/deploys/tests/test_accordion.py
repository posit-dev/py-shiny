import os
import pytest
from utils.deploy_utils import deploy
from playwright.sync_api import Page
from utils.express_utils import verify_express_accordion

APP_DIR = "shiny-express-accordion"
APP_NAME = "shiny_express_accordion"
PAGE_TIMEOUT = 120 * 1000
EXPECT_TIMEOUT = 30 * 1000
current_dir = os.path.dirname(os.path.abspath(__file__))
app_file_path = os.path.join(os.path.dirname(current_dir), "apps", APP_DIR)


@pytest.mark.integrationtest
@pytest.mark.only_browser("chromium")
@pytest.mark.parametrize("location", ["connect"])
def test_express_accordion(page: Page, location: str) -> None:
    page_url = deploy(location, APP_NAME, app_file_path)
    page.goto(page_url, timeout=PAGE_TIMEOUT)
    verify_express_accordion(page)
