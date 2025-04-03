from __future__ import annotations

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    df = controller.OutputDataFrame(page, "df1")
    df.expect_nrow(2)
    df.expect_ncol(3)
    df.expect_column_labels(["", "A", " "])

    df.expect_cell("1", row=0, col=0)
    df.expect_cell("2", row=1, col=0)
    df.expect_cell("4", row=0, col=1)
    df.expect_cell("8", row=1, col=2)
