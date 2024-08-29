import pytest
from playwright.sync_api import Page
from utils.deploy_utils import (
    local_deploys_app_url_fixture,
    reruns,
    reruns_delay,
    skip_if_not_chrome,
)

from shiny.playwright import controller

app_url = local_deploys_app_url_fixture("shiny-express-dataframe")


@skip_if_not_chrome
@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
def test_express_dataframe_deploys(page: Page, app_url: str) -> None:
    page.goto(app_url)

    dataframe = controller.OutputDataFrame(page, "sample_data_frame")
    dataframe.expect_nrow(6)
