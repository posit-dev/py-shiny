from conftest import ShinyAppProc
from controls import Sidebar, OutputTextVerbatim
from playwright.sync_api import Page


def test_express_page_sidebar(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    sidebar = Sidebar(page, "sidebar")
    sidebar.expect_text("SidebarTitle 'Sidebar Content'")
    output_txt = OutputTextVerbatim(page, "txt")
    output_txt.expect_value("50")

