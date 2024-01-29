from playwright.sync_api import Page, expect
from utils.deploy_utils import (
    create_deploys_app_url_fixture,
    skip_if_not_python_310_or_chrome,
)

app_url = create_deploys_app_url_fixture(__file__, "example_deploy_app_A")


@skip_if_not_python_310_or_chrome
def test_deploys(page: Page, app_url: str) -> None:
    if "127.0.0.1" not in app_url:
        page.set_default_timeout(120 * 1000)
    page.goto(app_url)

    COUNTRY = "Afghanistan"
    expect(page.get_by_text(COUNTRY)).to_have_count(1)
    page.get_by_role("cell", name=COUNTRY).click()
    expect(page.locator("#country_detail_pop")).to_contain_text(COUNTRY)
    expect(page.locator("#country_detail_percap")).to_contain_text(COUNTRY)
    expect(page.get_by_text(COUNTRY)).to_have_count(3)
