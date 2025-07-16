import pytest
from playwright.sync_api import Page, expect
from utils.deploy_utils import (
    local_deploys_app_url_fixture,
    reruns,
    reruns_delay,
    skip_if_not_chrome,
)

from shiny.playwright import controller

TIMEOUT = 2 * 60 * 1000

app_url = local_deploys_app_url_fixture("shiny_express_page_default")


@skip_if_not_chrome
@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
def test_page_default(page: Page, app_url: str) -> None:
    page.goto(app_url)

    # since it is a custom table we can't use the OutputTable controls
    expect(page.locator("#shell")).to_have_text(
        "R1C1R1\nR1C1R2-R1C1R1\nR1C1R2-R1C1R2\nR1C1R2-R1C2\nR1C2", timeout=TIMEOUT
    )

    # Perform these tests second as their locators are not stable over time.
    # (They require that a locator be realized before finding the second locator)
    nav_html = controller.NavsetTab(page, "express_navset_tab")
    nav_html._expect_content_text("pre 0pre 1pre 2")
    nav_html.set("div")
    nav_html._expect_content_text("div 0\ndiv 1\ndiv 2")
    nav_html.set("span")
    nav_html._expect_content_text("span 0span 1span 2")

    navset_card_tab = controller.NavsetTab(page, "express_navset_card_tab")
    navset_card_tab._expect_content_text("")
