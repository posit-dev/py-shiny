import os

import pytest
from playwright.sync_api import Page
from utils.deploy_utils import deploy, write_requirements_txt
from utils.express_utils import verify_express_page_fillable

APP_DIR = "shiny-express-page-fillable"
APP_NAME = "express_page_fillable"
# reqd since the app on connect takes a while to load
PAGE_TIMEOUT = 120 * 1000
EXPECT_TIMEOUT = 30 * 1000


current_dir = os.path.dirname(os.path.abspath(__file__))
app_file_path = os.path.join(os.path.dirname(current_dir), "apps", APP_DIR)


@pytest.mark.integrationtest
@pytest.mark.only_browser("chromium")
@pytest.mark.parametrize("location", ["connect", "shinyapps"])
def test_express_page_fillable(page: Page, location: str) -> None:
    write_requirements_txt(app_file_path)
    page_url = deploy(location, APP_NAME, app_file_path)
    page.goto(page_url, timeout=PAGE_TIMEOUT)
    verify_express_page_fillable(page)
