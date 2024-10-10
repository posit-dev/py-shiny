from __future__ import annotations

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_update_cell_value(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    pd_df = controller.OutputDataFrame(page, "pd_df")
    pd_df.expect_cell("PAL0708", row=0, col=0)

    pl_df = controller.OutputDataFrame(page, "pl_df")
    pl_df.expect_cell("PAL0708", row=0, col=0)

    pd_btn = controller.InputActionButton(page, "update_pd_btn")
    pl_btn = controller.InputActionButton(page, "update_pl_btn")

    # Update pandas
    pd_btn.click()
    pd_df.expect_cell("pandas - 1", row=0, col=0)
    pl_df.expect_cell("PAL0708", row=0, col=0)

    # Update polars
    pl_btn.click()
    pl_btn.click()
    pl_btn.click()

    pd_df.expect_cell("pandas - 1", row=0, col=0)
    pl_df.expect_cell("polars - 3", row=0, col=0)

    # Verify other cells do not change
    pd_df.expect_cell("PAL0708", row=1, col=0)
    pd_df.expect_cell("1", row=0, col=1)
    pd_df.expect_cell("2", row=1, col=1)

    pl_df.expect_cell("PAL0708", row=1, col=0)
    pl_df.expect_cell("1", row=0, col=1)
    pl_df.expect_cell("2", row=1, col=1)
