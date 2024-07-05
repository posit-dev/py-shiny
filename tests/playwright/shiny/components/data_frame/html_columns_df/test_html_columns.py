from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.render._data_frame import ColumnFilterNumber, ColumnFilterStr
from shiny.run import ShinyAppProc


def test_validate_html_columns(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    data_frame = controller.OutputDataFrame(page, "penguins_df")

    # verify shiny reactive output UI in cell
    output_txt = controller.OutputTextVerbatim(page, "test_cell_text")
    output_txt.expect_value("test_cell_value 0")
    test_button = controller.InputActionButton(page, "test_cell_button")
    test_button.click()
    output_txt.expect_value("test_cell_value 1")

    # assert patching works
    data_frame.expect_cell("N1A1", row=0, col=6)
    data_frame.save_cell("N1A11", row=0, col=6, save_key="Enter")
    data_frame.expect_cell("ID: N1A11", row=0, col=6)

    # assert sorting works
    data_frame.expect_cell("1", row=0, col=1)
    data_frame.set_sort(1)
    data_frame.expect_cell("152", row=0, col=1)

    # if a column is sorted, editing should not change the order
    data_frame.save_cell("152", row=0, col=1, save_key="Enter")
    data_frame.expect_cell("151", row=1, col=1)

    # assert HTMLDependency works by verifying javascript variable
    test_value = page.evaluate("window.shinytestvalue")
    assert test_value == "testing"

    # # sorting should not work for columns that are HTML columns
    data_frame.set_sort(3)
    data_frame.expect_cell("152", row=0, col=1)

    # reset the sorting for column
    data_frame.set_sort(1)
    data_frame.expect_cell("1", row=0, col=1)

    # filter by Individual IDs
    filter_text: ColumnFilterStr = {"col": 6, "value": "N2"}
    data_frame.set_filter(filter_text)
    data_frame.expect_cell("3", row=0, col=1)

    # respect filtering even after edits when filters have been applied
    data_frame.save_cell("3", row=0, col=1, save_key="Enter")
    data_frame.expect_cell("4", row=1, col=1)

    # assert that html columns are not editable
    data_frame.expect_cell_class("cell-html", row=1, col=0)
    data_frame.expect_cell_class("cell-html", row=0, col=2)
    data_frame.expect_cell_class("cell-html", row=0, col=3)
    data_frame.expect_cell_class("cell-html", row=0, col=4)
    data_frame.expect_cell_class("cell-html", row=0, col=0)

    data_frame.cell_locator(row=0, col=0).click()
    # Verify the class does not change to editing when a cell under a HTML column is clicked
    data_frame.expect_cell_class("cell-html", row=0, col=0)

    # Filter using a range for a column that contains numbers
    filter_num_range: ColumnFilterNumber = {"col": 1, "value": (40, 50)}
    data_frame.set_filter(filter_num_range)
    data_frame.expect_cell("40", row=0, col=1)

    # Editing a cell in the first row and hitting `shift+enter` should not submit the change and stay editing the current cell
    data_frame.expect_cell("N25A2", row=0, col=6)
    data_frame.save_cell("NAAAAA", row=0, col=6, save_key="Shift+Enter")
    data_frame.expect_cell("N25A2", row=0, col=6)
    data_frame.save_cell("NAAAAA", row=0, col=6, save_key="Escape")
    data_frame.expect_cell("N25A2", row=0, col=6)

    # Editing a cell in the last row and hitting `enter` should not submit the change and stay editing the current cell
    # data_frame.set_column_filter(7, text="No")
    # Test scrolling to last row
    data_frame.save_cell("NAAAAA", row=7, col=6, save_key="Enter")
    data_frame.expect_cell("N29A2", row=7, col=6)
    data_frame.save_cell("NAAAAA", row=7, col=6, save_key="Escape")
    data_frame.expect_cell("N29A2", row=7, col=6)

    # Test scrolling up to top
    data_frame.expect_cell("N25A2", row=0, col=6)
