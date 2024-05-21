from conftest import ShinyAppProc
from controls import InputActionButton, OutputCode, OutputDataFrame
from playwright.sync_api import Page


def test_dataframe_organization_methods(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    data_frame = OutputDataFrame(page, "iris_df")
    input_view_rows = OutputCode(page, "data_view_rows")
    input_view_selected_true = OutputCode(page, "data_view_selected_true")
    input_view_selected_false = OutputCode(page, "data_view_selected_false")
    input_cell_selection = OutputCode(page, "cell_selection")
    reset_df = InputActionButton(page, "reset_df")

    def reset_data_frame():
        reset_df.click()
        input_view_rows.expect_value("(0, 1, 2, 3, 4, 5)")
        input_view_selected_true.expect_value("[]")
        input_view_selected_false.expect_value("[  0   1  50  51 100 101]")
        input_cell_selection.expect_value("()")

    # assert value of unsorted table
    reset_data_frame()

    # sort column by number descending
    data_frame.set_column_sort(col=0)
    input_view_rows.expect_value("(2, 3, 4, 5, 0, 1)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[ 50  51 100 101   0   1]")
    input_cell_selection.expect_value("()")

    # sort column by number ascending
    data_frame.set_column_sort(col=0)
    input_view_rows.expect_value("(1, 0, 5, 4, 3, 2)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[  1   0 101 100  51  50]")
    input_cell_selection.expect_value("()")

    # sort column by text ascending
    data_frame.set_column_sort(col=4)
    input_view_rows.expect_value("(0, 1, 2, 3, 4, 5)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[  0   1  50  51 100 101]")
    input_cell_selection.expect_value("()")

    # sort column by text descending
    data_frame.set_column_sort(col=4)
    input_view_rows.expect_value("(4, 5, 2, 3, 0, 1) ")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[100 101  50  51   0   1]")
    input_cell_selection.expect_value("()")

    # filter using numbers
    reset_data_frame()
    data_frame.set_column_filter(col=0, text=["6", "6.9"])
    input_view_rows.expect_value("(3, 4)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[ 51 100]")
    input_cell_selection.expect_value("()")
    # filter programatically
    reset_data_frame()
    InputActionButton(page, "update_filter").click()
    input_view_rows.expect_value("(3, 4, 5)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[  51 100 101]")
    input_cell_selection.expect_value("()")

    data_frame.set_column_sort(3)
    input_view_rows.expect_value("(4, 5, 3)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[100 101  51]")
    input_cell_selection.expect_value("()")

    # select single row
    reset_data_frame()
    data_frame.select_rows([1])
    input_view_rows.expect_value("(0, 1, 2, 3, 4, 5)")
    input_view_selected_true.expect_value("[1]")
    input_view_selected_false.expect_value("[  0   1  50  51 100 101]")
    input_cell_selection.expect_value("(1,)")

    # sort columns programmatically
    reset_data_frame()
    InputActionButton(page, "update_sort").click()
    input_view_rows.expect_value("(0, 4, 3, 2, 1, 5)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[  0 100  51  50   1 101]")
    input_cell_selection.expect_value("()")

    # select multiple rows
    data_frame.select_rows([3, 1])  # select rows 3 and 1 of (0, 4, 3, 2, 1, 5)
    input_view_rows.expect_value("(0, 4, 3, 2, 1, 5) ")
    input_view_selected_true.expect_value("[100  50]")
    input_view_selected_false.expect_value("[  0 100  51  50   1 101]")
    input_cell_selection.expect_value("(4, 2)")
