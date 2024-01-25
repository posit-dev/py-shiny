import os

import pytest
from controls import OutputDataFrame
from playwright.sync_api import Page
from utils.deploy_utils import (
    deploy_locations,
    prepare_deploy_and_open_url,
    skip_if_not_python_310,
)

APP_NAME = "shiny-express-dataframe"
app_file_path = os.path.dirname(os.path.abspath(__file__))


@skip_if_not_python_310
@pytest.mark.only_browser("chromium")
@pytest.mark.parametrize("location", deploy_locations)
def test_express_dataframe_deploys(page: Page, location: str) -> None:
    prepare_deploy_and_open_url(page, app_file_path, location, APP_NAME)

    dataframe = OutputDataFrame(page, "sample_data_frame")
    dataframe.expect_n_row(6)
