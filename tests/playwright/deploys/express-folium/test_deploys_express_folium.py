from playwright.sync_api import Page, expect
from utils.deploy_utils import create_deploys_app_url_fixture, skip_if_not_chrome

app_url = create_deploys_app_url_fixture("shiny-express-folium")


@skip_if_not_chrome
def test_folium_map(page: Page, app_url: str) -> None:
    page.goto(app_url)

    expect(page.get_by_text("Static Map")).to_have_count(1)
    expect(page.get_by_text("Map inside of render express call")).to_have_count(1)
    # map inside the @render.express
    expect(
        page.frame_locator("iframe").nth(1).get_by_role("link", name="OpenStreetMap")
    ).to_have_count(1)
    # map outside of the @render.express at the top level
    expect(
        page.frame_locator("iframe")
        .nth(0)
        .get_by_role("link", name="U.S. Geological Survey")
    ).to_have_count(1)
