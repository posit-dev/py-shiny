from controls import Card, OutputTextVerbatim
from playwright.sync_api import Page
from utils.deploy_utils import create_deploys_app_url_fixture, skip_if_not_chrome

app_url = create_deploys_app_url_fixture("express_page_fluid")


@skip_if_not_chrome
def test_express_page_fluid(page: Page, app_url: str) -> None:
    page.goto(app_url)

    card = Card(page, "card")
    output_txt = OutputTextVerbatim(page, "txt")
    output_txt.expect_value("50")
    bounding_box = card.loc.bounding_box()
    assert bounding_box is not None
    assert bounding_box["height"] < 300
