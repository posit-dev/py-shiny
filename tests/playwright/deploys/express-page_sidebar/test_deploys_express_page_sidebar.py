from controls import OutputTextVerbatim, Sidebar
from playwright.sync_api import Page
from utils.deploy_utils import create_deploys_app_url_fixture, skip_if_not_chrome
from utils.express_utils import compare_annotations

from shiny import ui
from shiny.express import ui as xui

app_url = create_deploys_app_url_fixture("express_page_sidebar")


@skip_if_not_chrome
def test_express_page_sidebar(page: Page, app_url: str) -> None:
    page.goto(app_url)

    sidebar = Sidebar(page, "sidebar")
    sidebar.expect_text("SidebarTitle Sidebar Content")
    output_txt = OutputTextVerbatim(page, "txt")
    output_txt.expect_value("50")
    compare_annotations(ui.sidebar, xui.sidebar)
