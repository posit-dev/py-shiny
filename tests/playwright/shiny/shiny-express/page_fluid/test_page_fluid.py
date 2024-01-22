from conftest import ShinyAppProc, create_deploys_fixture
from playwright.sync_api import Page
from utils.express_utils import verify_express_page_fluid

app = create_deploys_fixture("shiny-express-page-fluid")


def test_express_page_fluid(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)
    verify_express_page_fluid(page)
