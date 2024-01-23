import os

import pytest
from conftest import ShinyAppProc
from controls import OutputDataFrame
from playwright.sync_api import Page
from utils.deploy_utils import prepare_deploy_and_open_url

APP_NAME = "shiny-express-dataframe"
app_file_path = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.only_browser("chromium")
@pytest.mark.parametrize("location", ["connect", "shinyapps", "local"])
def test_express_dataframe_deploys(
    page: Page, location: str, local_app: ShinyAppProc
) -> None:
    if location == "local":
        page.goto(local_app.url)
    else:
        prepare_deploy_and_open_url(page, app_file_path, location, APP_NAME)
    dataframe = OutputDataFrame(page, "sample_data_frame")
    dataframe.expect_n_row(6)
