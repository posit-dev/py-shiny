from conftest import ShinyAppProc, create_deploys_fixture
from playwright.sync_api import Page
from utils.express_utils import verify_express_accordion

app = create_deploys_fixture("shiny-express-accordion")


def test_express_accordion(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)
    verify_express_accordion(page)
