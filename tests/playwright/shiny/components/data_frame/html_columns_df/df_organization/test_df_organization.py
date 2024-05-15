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
        input_view_rows.expect_value("(0, 1, 2)")
        input_view_selected_true.expect_value("[]")
        input_view_selected_false.expect_value("[ 0 50 100]")
        input_cell_selection.expect_value("()")

    # assert value of unsorted table
    reset_data_frame()

    # sort column by number descending
    data_frame.set_column_sort(col=0)
    input_view_rows.expect_value("(1, 2, 0)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[ 50 100   0]")
    input_cell_selection.expect_value("()")

    # sort column by number ascending
    data_frame.set_column_sort(col=0)
    input_view_rows.expect_value("(0, 2, 1)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[ 0 100 50]")
    input_cell_selection.expect_value("()")

    # sort column by text ascending
    data_frame.set_column_sort(col=4)
    input_view_rows.expect_value("(0, 1, 2)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[ 0 50 100]")
    input_cell_selection.expect_value("()")

    # sort column by text descending
    data_frame.set_column_sort(col=4)
    input_view_rows.expect_value("(2, 1, 0)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[100 50  0]")
    input_cell_selection.expect_value("()")

    reset_data_frame()

    # filter using numbers
    data_frame.set_column_filter(col=0, text=["6", "7"])
    input_view_rows.expect_value("(1, 2)")
    input_view_selected_true.expect_value("[]")
    input_view_selected_false.expect_value("[ 50 100]")
    input_cell_selection.expect_value("()")

    reset_data_frame()

    # select multiple rows
    data_frame.select_rows([0, 2])
    input_view_rows.expect_value("(0, 1, 2)")
    input_view_selected_true.expect_value("[  0 100]")
    input_view_selected_false.expect_value("[  0  50 100]")
    input_cell_selection.expect_value("(0, 2)")

    reset_data_frame()

    # select single row
    data_frame.select_rows([0])
    input_view_rows.expect_value("(0, 1, 2)")
    input_view_selected_true.expect_value("[0]")
    input_view_selected_false.expect_value("[  0  50 100]")
    input_cell_selection.expect_value("(0,)")
