import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.render._data_frame_utils._types import ColumnFilterNumber
from shiny.run import ShinyAppProc


@pytest.mark.parametrize("tab_name", ["pandas", "polars"])
def test_dataframe_methods(page: Page, local_app: ShinyAppProc, tab_name: str) -> None:

    page.goto(local_app.url)

    tab = controller.NavsetUnderline(page, "tab")
    tab.set(tab_name)

    data_frame = controller.OutputDataFrame(page, f"{tab_name}-iris_df")
    data_view_rows = controller.OutputCode(page, f"{tab_name}-data_view_rows")
    data_view_selected_true = controller.OutputCode(
        page, f"{tab_name}-data_view_selected_true"
    )
    data_view_selected_false = controller.OutputCode(
        page, f"{tab_name}-data_view_selected_false"
    )
    cell_selection = controller.OutputCode(page, f"{tab_name}-cell_selection")
    reset_df = controller.InputActionButton(page, f"{tab_name}-reset_df")
    update_sort = controller.InputActionButton(page, f"{tab_name}-update_sort")
    update_filter = controller.InputActionButton(page, f"{tab_name}-update_filter")

    def reset_data_frame():
        reset_df.click()
        data_view_rows.expect_value("(0, 1, 2, 3, 4, 5)")
        data_view_selected_true.expect_value("[]")
        data_view_selected_false.expect_value("[0, 1, 50, 51, 100, 101]")
        cell_selection.expect_value("()")

    # assert value of unsorted table
    reset_data_frame()

    # sort column by number descending
    data_frame.set_sort(0)
    data_view_rows.expect_value("(2, 3, 4, 5, 0, 1)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[50, 51, 100, 101, 0, 1]")
    cell_selection.expect_value("()")

    # sort column by number ascending
    data_frame.set_sort({"col": 0, "desc": False})
    data_view_rows.expect_value("(1, 0, 5, 4, 3, 2)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[1, 0, 101, 100, 51, 50]")
    cell_selection.expect_value("()")

    # sort column by text ascending
    data_frame.set_sort([4])
    data_view_rows.expect_value("(0, 1, 2, 3, 4, 5)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[0, 1, 50, 51, 100, 101]")
    cell_selection.expect_value("()")

    # sort column by text descending
    data_frame.set_sort({"col": 4, "desc": True})
    data_view_rows.expect_value("(4, 5, 2, 3, 0, 1) ")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[100, 101, 50, 51, 0, 1]")
    cell_selection.expect_value("()")

    reset_data_frame()

    # filter using numbers
    filter_num_range: ColumnFilterNumber = {"col": 0, "value": [6, 6.9]}
    data_frame.set_filter(filter_num_range)
    data_view_rows.expect_value("(3, 4)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[51, 100]")
    cell_selection.expect_value("()")
    # filter programmatically
    reset_data_frame()
    update_filter.click()
    data_view_rows.expect_value("(3, 4, 5)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[51, 100, 101]")
    cell_selection.expect_value("()")

    data_frame.set_sort(3)
    data_view_rows.expect_value("(4, 5, 3)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[100, 101, 51]")
    cell_selection.expect_value("()")

    # select single row
    reset_data_frame()
    data_frame.select_rows([1])
    data_view_rows.expect_value("(0, 1, 2, 3, 4, 5)")
    data_view_selected_true.expect_value("[1]")
    data_view_selected_false.expect_value("[0, 1, 50, 51, 100, 101]")
    cell_selection.expect_value("(1,)")

    reset_data_frame()

    # sort columns programmatically
    update_sort.click()
    data_view_rows.expect_value("(0, 4, 3, 2, 1, 5)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[0, 100, 51, 50, 1, 101]")
    cell_selection.expect_value("()")

    # select multiple rows
    data_frame.select_rows([3, 1])  # select rows 3 and 1 of (0, 4, 3, 2, 1, 5)
    data_view_rows.expect_value("(0, 4, 3, 2, 1, 5) ")
    data_view_selected_true.expect_value("[100, 50]")
    data_view_selected_false.expect_value("[0, 100, 51, 50, 1, 101]")
    cell_selection.expect_value("(4, 2)")
