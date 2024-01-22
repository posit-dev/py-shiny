from conftest import ShinyAppProc, create_deploys_fixture
from playwright.sync_api import Page
from utils.express_utils import verify_express_dataframe

app = create_deploys_fixture("shiny-express-dataframe")


def test_page_default(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)
    verify_express_dataframe(page)
