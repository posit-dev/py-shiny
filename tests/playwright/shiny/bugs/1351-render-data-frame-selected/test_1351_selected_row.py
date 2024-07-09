from __future__ import annotations

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    df = controller.OutputDataFrame(page, "df1")
    add_row = controller.InputActionButton(page, "add_row")
    clear_table = controller.InputActionButton(page, "clear_table")
    selected_rows = controller.OutputTextVerbatim(page, "number_of_selected_rows")

    df.expect_nrow(0)
    selected_rows.expect_value("Selected rows: 0")

    add_row.click()

    df.expect_nrow(1)
    selected_rows.expect_value("Selected rows: 0")

    df.cell_locator(0, 0).click()
    df.select_rows([0])

    df.expect_nrow(1)
    selected_rows.expect_value("Selected rows: 1")

    clear_table.click()
    selected_rows.expect_value("Selected rows: 0")

    bad_error_lines = [line for line in local_app.stderr._lines if "INFO:" not in line]
    assert len(bad_error_lines) == 0, bad_error_lines
