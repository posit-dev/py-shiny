import os

import pytest
from conftest import ShinyAppProc
from controls import OutputTextVerbatim, Sidebar
from playwright.sync_api import Page
from utils.deploy_utils import prepare_deploy_and_open_url
from utils.express_utils import compare_annotations

from shiny import ui
from shiny.express import ui as xui

APP_NAME = "express_page_sidebar"
app_file_path = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.only_browser("chromium")
@pytest.mark.parametrize("location", ["connect", "shinyapps", "local"])
def test_express_page_sidebar(
    page: Page, location: str, local_app: ShinyAppProc
) -> None:
    if location == "local":
        page.goto(local_app.url)
    else:
        prepare_deploy_and_open_url(page, app_file_path, location, APP_NAME)
    sidebar = Sidebar(page, "sidebar")
    sidebar.expect_text("SidebarTitle Sidebar Content")
    output_txt = OutputTextVerbatim(page, "txt")
    output_txt.expect_value("50")
    compare_annotations(ui.sidebar, xui.sidebar)
