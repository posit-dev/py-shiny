from shiny.test import Page, ShinyAppProc
from shiny.test._controls import InputActionButton, OutputCode, OutputDataFrame


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
        data_view_rows.expect_value("(0, 1, 2)")
        data_view_selected_true.expect_value("[]")
        data_view_selected_false.expect_value("[ 0 50 100]")
        cell_selection.expect_value("()")

    # assert value of unsorted table
    reset_data_frame()

    # sort column by number descending
    data_frame.set_column_sort(col=0)
    data_view_rows.expect_value("(1, 2, 0)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[ 50 100   0]")
    cell_selection.expect_value("()")

    # sort column by number ascending
    data_frame.set_column_sort(col=0)
    data_view_rows.expect_value("(0, 2, 1)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[ 0 100 50]")
    cell_selection.expect_value("()")

    # sort column by text ascending
    data_frame.set_column_sort(col=4)
    data_view_rows.expect_value("(0, 1, 2)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[ 0 50 100]")
    cell_selection.expect_value("()")

    # sort column by text descending
    data_frame.set_column_sort(col=4)
    data_view_rows.expect_value("(2, 1, 0)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[100 50  0]")
    cell_selection.expect_value("()")

    reset_data_frame()

    # filter using numbers
    data_frame.set_column_filter(col=0, text=["6", "7"])
    data_view_rows.expect_value("(1, 2)")
    data_view_selected_true.expect_value("[]")
    data_view_selected_false.expect_value("[ 50 100]")
    cell_selection.expect_value("()")

    reset_data_frame()

    # select multiple rows
    data_frame.select_rows([0, 2])
    data_view_rows.expect_value("(0, 1, 2)")
    data_view_selected_true.expect_value("[  0 100]")
    data_view_selected_false.expect_value("[  0  50 100]")
    cell_selection.expect_value("(0, 2)")

    reset_data_frame()

    # select single row
    data_frame.select_rows([0])
    data_view_rows.expect_value("(0, 1, 2)")
    data_view_selected_true.expect_value("[0]")
    data_view_selected_false.expect_value("[  0  50 100]")
    cell_selection.expect_value("(0,)")
