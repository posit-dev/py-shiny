import os

import pytest
from conftest import ShinyAppProc
from controls import Card, OutputTextVerbatim
from playwright.sync_api import Page
from utils.deploy_utils import prepare_deploy_and_open_url, skip_if_not_python_310

APP_NAME = "express_page_fluid"
app_file_path = os.path.dirname(os.path.abspath(__file__))


@skip_if_not_python_310
@pytest.mark.only_browser("chromium")
@pytest.mark.parametrize("location", ["connect", "shinyapps", "local"])
def test_express_page_fluid(page: Page, location: str, local_app: ShinyAppProc) -> None:
    if location == "local":
        page.goto(local_app.url)
    else:
        prepare_deploy_and_open_url(page, app_file_path, location, APP_NAME)
    card = Card(page, "card")
    output_txt = OutputTextVerbatim(page, "txt")
    output_txt.expect_value("50")
    bounding_box = card.loc.bounding_box()
    assert bounding_box is not None
    assert bounding_box["height"] < 300
