from conftest import ShinyAppProc
from controls import OutputDataFrame
from playwright.sync_api import Page


def test_validate_html_columns(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    data_frame = OutputDataFrame(page, "penguins_df")

    # assert patching works
    data_frame.expect_cell("N1A1", row=1, col=7)
    data_frame.save_cell("N1A11", row=1, col=7, save_key="Enter")
    data_frame.expect_cell("ID: N1A11", row=1, col=7)
    data_frame.expect_cell("1", row=1, col=2)
    data_frame.expect_cell("1", row=1, col=2)
    data_frame.sort_column(col=2)
    data_frame.expect_cell("152", row=1, col=2)
    # if a column is sorted, editing should not change the order
    data_frame.save_cell("152", row=1, col=2, save_key="Enter")
    data_frame.expect_cell("151", row=2, col=2)

    # reset the sorting for column
    data_frame.sort_column(col=2)
    data_frame.expect_cell("1", row=1, col=2)

    # sorting should not work for columns that are HTML columns
    data_frame.sort_column(col=3)
    data_frame.expect_cell("1", row=1, col=2)

    # filter by Individual IDs
    data_frame.filter_column(7, text="N2")
    data_frame.expect_cell("3", row=1, col=2)

    # respect filtering even after edits when filters have been applied
    data_frame.save_cell("3", row=1, col=2, save_key="Enter")
    data_frame.expect_cell("4", row=2, col=2)

    # assert that html columns are not editable
    data_frame.expect_cell_class("cell-html", row=1, col=3)
    data_frame.expect_cell_class("cell-html", row=1, col=4)
    data_frame.expect_cell_class("cell-html", row=1, col=5)
    data_frame.expect_cell_class("cell-html", row=1, col=1)

    # cannot edit HTML columns
    data_frame.save_cell("3", row=1, col=3, save_key="Enter")
