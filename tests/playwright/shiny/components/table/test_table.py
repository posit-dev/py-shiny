import re

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_table_data_support(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # The first expectation after page load absorbs the initial render flush,
    # which can exceed the default 5s timeout on a loaded CI runner.
    controller.OutputTable(page, "nw_table").expect_nrow(2, timeout=30 * 1000)
    controller.OutputCode(page, "nw_df_type").expect_value(re.compile("narwhals"))

    controller.OutputTable(page, "pd_table").expect_nrow(2)
    controller.OutputCode(page, "pd_df_type").expect_value(re.compile("pandas"))
