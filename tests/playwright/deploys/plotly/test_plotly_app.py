from playwright.sync_api import Page, expect
from utils.deploy_utils import create_deploys_app_url_fixture, skip_if_not_chrome

TIMEOUT = 2 * 60 * 1000
app_url = create_deploys_app_url_fixture("example_deploy_app_A")


@skip_if_not_chrome
def test_deploys(page: Page, app_url: str) -> None:
    page.goto(app_url)

    COUNTRY = "Afghanistan"
    expect(page.get_by_text(COUNTRY)).to_have_count(1, timeout=TIMEOUT)
    page.get_by_role("cell", name=COUNTRY).click()
    expect(page.locator("#country_detail_pop")).to_contain_text(
        COUNTRY, timeout=TIMEOUT
    )
    expect(page.locator("#country_detail_percap")).to_contain_text(COUNTRY)
    expect(page.get_by_text(COUNTRY)).to_have_count(3)
