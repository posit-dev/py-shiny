from __future__ import annotations

from shiny.test import Page, ShinyAppProc
from shiny.test._controls import OutputDataFrame, OutputTextVerbatim


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    df = OutputDataFrame(page, "df1")
    selected_rows = OutputTextVerbatim(page, "selected_rows")
    cell_selection = OutputTextVerbatim(page, "cell_selection")

    df.expect_n_row(3)
    selected_rows.expect_value("Input selected rows: ()")
    cell_selection.expect_value("Cell selection rows: ()")

    df.select_rows([0, 2])

    selected_rows.expect_value("Input selected rows: (0, 2)")
    cell_selection.expect_value("Cell selection rows: (0, 2)")
