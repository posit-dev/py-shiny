from controls import LayoutNavsetTab
from playwright.sync_api import Page, expect
from utils.deploy_utils import create_deploys_app_url_fixture, skip_if_not_chrome

TIMEOUT = 2 * 60 * 1000

app_url = create_deploys_app_url_fixture("shiny_express_page_default")


@skip_if_not_chrome
def test_page_default(page: Page, app_url: str) -> None:
    page.goto(app_url)

    # since it is a custom table we can't use the OutputTable controls
    expect(page.locator("#shell")).to_have_text(
        "R1C1R1\nR1C1R2-R1C1R1\nR1C1R2-R1C1R2\nR1C1R2-R1C2\nR1C2", timeout=TIMEOUT
    )

    # Perform these tests second as their locators are not stable over time.
    # (They require that a locator be realized before finding the second locator)
    nav_html = LayoutNavsetTab(page, "express_navset_tab")
    nav_html.expect_content("pre 0pre 1pre 2")
    nav_html.set("div")
    nav_html.expect_content("div 0\ndiv 1\ndiv 2")
    nav_html.set("span")
    nav_html.expect_content("span 0span 1span 2")

    navset_card_tab = LayoutNavsetTab(page, "express_navset_card_tab")
    navset_card_tab.expect_content("")
