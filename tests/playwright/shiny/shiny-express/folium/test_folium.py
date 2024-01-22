from conftest import ShinyAppProc, create_deploys_fixture
from playwright.sync_api import Page
from utils.express_utils import verify_express_folium_render

app = create_deploys_fixture("shiny-express-folium")


def test_folium_map(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)
    verify_express_folium_render(page)
