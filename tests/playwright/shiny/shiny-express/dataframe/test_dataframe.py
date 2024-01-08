from conftest import ShinyAppProc
from playwright.sync_api import Page
from utils.express_utils import verify_express_dataframe


def test_page_default(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    verify_express_dataframe(page)
