import pytest
from playwright.sync_api import Page
from utils.deploy_utils import (
    local_deploys_app_url_fixture,
    reruns,
    reruns_delay,
    skip_if_not_chrome,
)

from shiny.playwright import controller

app_url = local_deploys_app_url_fixture("express_page_fluid")


@skip_if_not_chrome
@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
def test_express_page_fluid(page: Page, app_url: str) -> None:
    page.goto(app_url)

    card = controller.Card(page, "card")
    output_txt = controller.OutputTextVerbatim(page, "txt")
    output_txt.expect_value("50")
    bounding_box = card.loc.bounding_box()
    assert bounding_box is not None
    assert bounding_box["height"] < 300
