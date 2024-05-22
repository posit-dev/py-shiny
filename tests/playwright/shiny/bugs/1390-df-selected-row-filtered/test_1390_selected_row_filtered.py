from __future__ import annotations

import platform

from conftest import ShinyAppProc
from controls import OutputDataFrame, OutputCode
from playwright.sync_api import Page, expect


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    my_df = OutputDataFrame(page, "my_df")
    selected_df = OutputDataFrame(page, "selected_df")
    selected_rows = OutputCode(page, "selected_rows")

    # TODO-karan-test: We should add a locator for selected rows
    # TODO-karan-test; We should add a expected selected row count method?
    def expect_selected_count(x: OutputDataFrame, n: int) -> None:
        expect(x.loc_body.locator("tr[aria-selected=true]")).to_have_count(n)

    my_df.expect_n_row(10)
    expect_selected_count(my_df, 0)
    selected_df.expect_n_row(0)
    selected_rows.expect_value("()")

    # Select row
    my_df.select_rows([5])
    my_df.expect_n_row(10)
    expect_selected_count(my_df, 1)
    selected_df.expect_n_row(1)
    selected_rows.expect_value("(5,)")

    # # Filter to different row
    # Currently this causes an error
    my_df.set_column_filter(0, text="5")
    my_df.expect_n_row(1)
    expect_selected_count(my_df, 1)
    selected_df.expect_n_row(1)
    selected_rows.expect_value("(5,)")
    # # Remove the filter
    my_df.set_column_filter(0, text="")
    # Confirm the original data frame returns
    my_df.expect_n_row(10)
    # Confirm the previous row is still selected as no new selection has been made
    expect_selected_count(my_df, 1)
    selected_df.expect_n_row(1)
    selected_rows.expect_value("(5,)")

    # Filter to non selected row
    # Currently this causes an error
    my_df.set_column_filter(0, text="7")
    my_df.expect_n_row(1)
    expect_selected_count(my_df, 0)
    selected_df.expect_n_row(0)
    selected_rows.expect_value("()")

    # Path forward: subset the selected rows

    # Remove the filter
    # Confirm the original data frame returns
    my_df.set_column_filter(0, text="")
    my_df.expect_n_row(10)
    expect_selected_count(my_df, 1)
    selected_df.expect_n_row(1)
    selected_rows.expect_value("(5,)")

    # Remove selection
    modifier = "Meta" if platform.system() == "Darwin" else "Control"
    my_df.cell_locator(row=5, col=0).click(
        modifiers=[modifier]
    )  # TODO-karan-test: Support unselect row method
    expect_selected_count(my_df, 0)
    selected_df.expect_n_row(0)
    selected_rows.expect_value("()")
