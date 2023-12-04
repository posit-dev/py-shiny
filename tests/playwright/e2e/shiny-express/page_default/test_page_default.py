from conftest import ShinyAppProc
from utils.express_utils import verify_express_page_default
from playwright.sync_api import Page


def test_express_accordion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    verify_express_page_default(page)
