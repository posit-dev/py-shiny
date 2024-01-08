from conftest import ShinyAppProc
from playwright.sync_api import Page
from utils.express_utils import verify_express_folium_render


def test_folium_map(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    verify_express_folium_render(page)
