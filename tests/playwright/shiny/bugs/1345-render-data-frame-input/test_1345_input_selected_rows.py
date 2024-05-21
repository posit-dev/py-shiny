from __future__ import annotations

from conftest import ShinyAppProc
from controls import OutputDataFrame, OutputTextVerbatim
from playwright.sync_api import Page


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    df = OutputDataFrame(page, "df1")
    selected_rows = OutputTextVerbatim(page, "selected_rows")
    cell_selection = OutputTextVerbatim(page, "cell_selection")

    df.expect_n_row(3)
    selected_rows.expect_value("Input selected rows: ()")
    cell_selection.expect_value("No cells selected")

    df.select_rows([0, 2])

    selected_rows.expect_value("Input selected rows: (0, 2)")
    cell_selection.expect_value("Cell selection rows: (0, 2)")
