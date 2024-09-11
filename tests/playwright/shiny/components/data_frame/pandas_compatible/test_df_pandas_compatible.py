import re

from playwright.sync_api import Page
from utils.deploy_utils import skip_on_python_version

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_python_version(
    "3.9",
    reason="Astropy (and numpy) hav difficulty loading on python 3.9. posit-dev/py-shiny#1678",
)
def test_data_frame_pandas_compatible(
    page: Page,
    local_app: ShinyAppProc,
) -> None:
    page.goto(local_app.url)

    controller.OutputCode(page, "code_original").expect_value(re.compile("astropy"))
    controller.OutputCode(page, "code_astropy").expect_value(re.compile("pandas"))
    controller.OutputCode(page, "code_data").expect_value(re.compile("pandas"))
