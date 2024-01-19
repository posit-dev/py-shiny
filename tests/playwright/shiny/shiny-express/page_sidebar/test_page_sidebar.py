from conftest import ShinyAppProc, create_deploys_fixture
from playwright.sync_api import Page
from utils.express_utils import verify_express_page_sidebar

app = create_deploys_fixture("shiny-express-page-sidebar")


def test_express_page_sidebar(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)
    verify_express_page_sidebar(page)
