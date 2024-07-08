from __future__ import annotations

import platform

from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.render._data_frame_utils._types import ColumnFilterStr
from shiny.run import ShinyAppProc


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    my_df = controller.OutputDataFrame(page, "my_df")
    selected_df = controller.OutputDataFrame(page, "selected_df")
    selected_rows = controller.OutputCode(page, "selected_rows")

    # TODO-karan-test: We should add a locator for selected rows
    # TODO-karan-test; We should add a expected selected row count method?
    def expect_selected_count(x: controller.OutputDataFrame, n: int) -> None:
        expect(x.loc_body.locator("tr[aria-selected=true]")).to_have_count(n)

    my_df.expect_nrow(10)
    expect_selected_count(my_df, 0)
    selected_df.expect_nrow(0)
    selected_rows.expect_value("()")

    # Select row
    my_df.select_rows([5, 7])
    my_df.expect_nrow(10)
    expect_selected_count(my_df, 2)
    selected_df.expect_nrow(2)
    selected_rows.expect_value("(5, 7)")

    filter_text: ColumnFilterStr = {"col": 0, "value": "5"}
    # # Filter to different row
    # Currently this causes an error
    my_df.set_filter(filter_text)
    my_df.expect_nrow(1)
    expect_selected_count(my_df, 1)
    selected_df.expect_nrow(1)
    selected_rows.expect_value("(5,)")
    # # Remove the filter
    my_df.set_filter(None)
    # Confirm the original data frame returns
    my_df.expect_nrow(10)
    # Confirm the previous row is still selected as no new selection has been made
    expect_selected_count(my_df, 2)
    selected_df.expect_nrow(2)
    selected_rows.expect_value("(5, 7)")

    # Filter to non selected row
    # Currently this causes an error
    filter_text["value"] = "8"
    filter_text["col"] = 0
    my_df.set_filter(filter_text)
    my_df.expect_nrow(1)
    expect_selected_count(my_df, 0)
    selected_df.expect_nrow(0)
    selected_rows.expect_value("()")

    # Remove the filter
    # Confirm the original data frame returns
    my_df.set_filter(None)
    my_df.expect_nrow(10)
    expect_selected_count(my_df, 2)
    selected_df.expect_nrow(2)
    selected_rows.expect_value("(5, 7)")

    # Update selection with new selection while under a filter
    my_df.set_filter(filter_text)
    my_df.expect_nrow(1)
    expect_selected_count(my_df, 0)
    selected_df.expect_nrow(0)
    selected_rows.expect_value("()")
    my_df.select_rows([0])
    my_df.set_filter(None)
    my_df.expect_nrow(10)
    expect_selected_count(my_df, 1)
    selected_df.expect_nrow(1)
    selected_rows.expect_value("(8,)")

    # Remove selection
    modifier = "Meta" if platform.system() == "Darwin" else "Control"
    for row in (8,):
        my_df.cell_locator(row=row, col=0).click(
            modifiers=[modifier]
        )  # TODO-karan-test: Support unselect row method
    expect_selected_count(my_df, 0)
    selected_df.expect_nrow(0)
    selected_rows.expect_value("()")
