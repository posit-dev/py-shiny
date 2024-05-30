from conftest import ShinyAppProc
from controls import InputActionButton, OutputCode, OutputDataFrame
from playwright.sync_api import Page


def test_dataframe_organization_methods(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    data_frame = OutputDataFrame(page, "iris_df")
    data_view_rows = OutputCode(page, "data_view_rows")
    data_view_selected_true = OutputCode(page, "data_view_selected_true")
    data_view_selected_false = OutputCode(page, "data_view_selected_false")
    cell_selection = OutputCode(page, "cell_selection")
    reset_df = InputActionButton(page, "reset_df")

    def reset_data_frame():
        reset_df.click()
        data_view_rows.expect_value("(0, 1, 2, 3, 4, 5)")
        data_view_selected_true.expect_value("[]")
        data_view_selected_false.expect_value("[  0   1  50  51 100 101]")
        cell_selection.expect_value("()")

    # assert value of unsorted table
    reset_data_frame()

    # sort column by number descending
    data_frame.set_column_sort(col=0)
    data_view_rows.expect_value("(2, 3, 4, 5, 0, 1)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[ 50  51 100 101   0   1]")
    cell_selection.expect_value("()")

    # sort column by number ascending
    data_frame.set_column_sort(col=0)
    data_view_rows.expect_value("(1, 0, 5, 4, 3, 2)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[  1   0 101 100  51  50]")
    cell_selection.expect_value("()")

    # sort column by text ascending
    data_frame.set_column_sort(col=4)
    data_view_rows.expect_value("(0, 1, 2, 3, 4, 5)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[  0   1  50  51 100 101]")
    cell_selection.expect_value("()")

    # sort column by text descending
    data_frame.set_column_sort(col=4)
    data_view_rows.expect_value("(4, 5, 2, 3, 0, 1) ")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[100 101  50  51   0   1]")
    cell_selection.expect_value("()")

    reset_data_frame()

    # filter using numbers
    data_frame.set_column_filter(col=0, text=["6", "6.9"])
    data_view_rows.expect_value("(3, 4)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[ 51 100]")
    cell_selection.expect_value("()")
    # filter programmatically
    reset_data_frame()
    InputActionButton(page, "update_filter").click()
    data_view_rows.expect_value("(3, 4, 5)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[  51 100 101]")
    cell_selection.expect_value("()")

    data_frame.set_column_sort(3)
    data_view_rows.expect_value("(4, 5, 3)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[100 101  51]")
    cell_selection.expect_value("()")

    # select single row
    reset_data_frame()
    data_frame.select_rows([1])
    data_view_rows.expect_value("(0, 1, 2, 3, 4, 5)")
    data_view_selected_true.expect_value("[1]")
    data_view_selected_false.expect_value("[  0   1  50  51 100 101]")
    cell_selection.expect_value("(1,)")

    reset_data_frame()

    # sort columns programmatically
    InputActionButton(page, "update_sort").click()
    data_view_rows.expect_value("(0, 4, 3, 2, 1, 5)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[  0 100  51  50   1 101]")
    cell_selection.expect_value("()")

    # select multiple rows
    data_frame.select_rows([3, 1])  # select rows 3 and 1 of (0, 4, 3, 2, 1, 5)
    data_view_rows.expect_value("(0, 4, 3, 2, 1, 5) ")
    data_view_selected_true.expect_value("[100  50]")
    data_view_selected_false.expect_value("[  0 100  51  50   1 101]")
    cell_selection.expect_value("(4, 2)")
