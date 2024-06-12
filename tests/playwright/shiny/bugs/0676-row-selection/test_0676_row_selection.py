from __future__ import annotations

from playwright.sync_api import Page, expect

from shiny.playwright.controls import OutputCode, OutputDataFrame
from shiny.run import ShinyAppProc


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # The purpose of this test is to make sure that the data grid can work on Pandas
    # data frames that use an index that is not simply 0-based integers.

    grid = OutputDataFrame(page, "grid")
    detail = OutputDataFrame(page, "detail")
    selected_rows = OutputCode(page, "selected_rows")

    grid.expect_cell("three", row=2, col=0)
    detail.expect_n_row(0)
    detail.expect_n_col(3)
    selected_rows.expect_value("()")

    grid.select_rows([2])
    detail.expect_n_row(1)
    detail.expect_cell("three", row=0, col=0)
    selected_rows.expect_value("(2,)")

    # Ensure that keys are in sorted order, not the order in which they were selected
    # row1.click(modifiers=["Shift"])
    grid.loc_body.locator("td").nth(0).click(modifiers=["Shift"])
    detail.expect_n_row(3)
    selected_rows.expect_value("(0, 1, 2)")
