import re

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_table_data_support(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    table = controller.OutputTable(page, "nw_table")

    table.expect_nrow(2)

    controller.OutputCode(page, "nw_df_type").expect_value(re.compile("narwhals"))
