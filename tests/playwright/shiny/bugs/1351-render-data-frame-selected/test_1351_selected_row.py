from __future__ import annotations

from conftest import ShinyAppProc
from controls import InputActionButton, OutputDataFrame, OutputTextVerbatim
from playwright.sync_api import Page


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    df = OutputDataFrame(page, "df1")
    add_row = InputActionButton(page, "add_row")
    clear_table = InputActionButton(page, "clear_table")
    selected_rows = OutputTextVerbatim(page, "number_of_selected_rows")

    df.expect_n_row(0)
    selected_rows.expect_value("Selected rows: 0")

    add_row.click()

    df.expect_n_row(1)
    selected_rows.expect_value("Selected rows: 0")

    df.cell_locator(0, 0).click()
    df.select_rows([0])

    df.expect_n_row(1)
    selected_rows.expect_value("Selected rows: 1")

    clear_table.click()
    selected_rows.expect_value("Selected rows: 0")

    bad_error_lines = [line for line in local_app.stderr._lines if "INFO:" not in line]
    assert len(bad_error_lines) == 0, bad_error_lines
