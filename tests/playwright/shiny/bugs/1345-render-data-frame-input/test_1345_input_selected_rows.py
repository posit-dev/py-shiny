from __future__ import annotations

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    df = controller.OutputDataFrame(page, "df1")
    selected_rows = controller.OutputTextVerbatim(page, "selected_rows")
    cell_selection = controller.OutputTextVerbatim(page, "cell_selection")

    df.expect_nrow(3)
    selected_rows.expect_value("Input selected rows: ()")
    cell_selection.expect_value("Cell selection rows: ()")

    df.select_rows([0, 2])

    selected_rows.expect_value("Input selected rows: (0, 2)")
    cell_selection.expect_value("Cell selection rows: (0, 2)")
