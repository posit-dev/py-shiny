import re

import pytest
from playwright.sync_api import Page
from utils.deploy_utils import skip_if_not_chrome

from shiny.playwright import controller
from shiny.render._data_frame import ColumnFilter
from shiny.run import ShinyAppProc


@skip_if_not_chrome
@pytest.mark.parametrize("df_type", ["pandas", "polars"])
def test_validate_html_columns(
    page: Page, local_app: ShinyAppProc, df_type: str
) -> None:
    page.goto(local_app.url)

    data_frame = controller.OutputDataFrame(page, f"{df_type}_df")

    tab = controller.NavsetCardUnderline(page, "tab")
    output_txt = controller.OutputTextVerbatim(page, f"{df_type}_test_cell_text")
    test_button = controller.InputActionButton(page, f"{df_type}_test_cell_button")

    tab.set(df_type)

    # verify shiny reactive output UI in cell
    # Add a larger timeout for CI
    output_txt.expect_value(f"{df_type}_test_cell_value 0", timeout=30 * 1000)

    # Test Shiny reactive output in cell
    test_button.click()
    output_txt.expect_value(f"{df_type}_test_cell_value 1")

    # Assert cell content is not "null", but `""`
    data_frame.expect_cell(re.compile(r"^$"), row=3, col=13)
    data_frame.expect_cell(re.compile(r"^$"), row=1, col=16)

    # assert patching works
    data_frame.expect_cell("N1A1", row=0, col=6)
    data_frame.set_cell("N1A11", row=0, col=6, finish_key="Enter")
    data_frame.expect_cell("ID: N1A11", row=0, col=6)

    # assert sorting works
    data_frame.expect_cell("1", row=0, col=1)
    data_frame.set_sort(1)  # sample
    data_frame.expect_cell("152", row=0, col=1)
    # confirm sorting is reset before setting
    data_frame.set_sort(1)  # sample
    data_frame.expect_cell("152", row=0, col=1)
    # confirm sorting is reset before setting
    data_frame.set_sort(13)  # sex
    data_frame.expect_cell("4", row=0, col=1)

    # sort with multiple columns
    data_frame.set_sort([8, 1])  # Date egg, sample
    data_frame.expect_cell("34", row=0, col=1)
    # Perform double sort, make sure extra clicks are made to sort the second sort column
    data_frame.set_sort([8, 9])  # Dat egg, Culmen Length (mm)
    data_frame.expect_cell("10", row=0, col=1)
    data_frame.set_sort([8, {"col": 9, "desc": False}])
    data_frame.expect_cell("9", row=0, col=1)
    # reset sorting
    data_frame.set_sort(None)
    data_frame.expect_cell("1", row=0, col=1)
    # set sorting for rest of tests
    data_frame.set_sort({"col": 1, "desc": True})
    data_frame.expect_cell("152", row=0, col=1)

    # if a column is sorted, editing should not change the order
    data_frame.set_cell("152", row=0, col=1, finish_key="Enter")
    data_frame.expect_cell("151", row=1, col=1)

    # assert HTMLDependency works by verifying javascript variable
    test_value = page.evaluate("window.shinytestvalue")
    assert test_value == "testing"

    # Sorting should not work for columns that are HTML columns
    # Verify that the sorting is reset
    with pytest.raises(AssertionError) as e:
        data_frame.set_sort(3, timeout=0)
        assert "header-html" in str(e)
    data_frame.expect_cell("1", row=0, col=1)

    # filter by Individual IDs
    filter_text: ColumnFilter = {"col": 6, "value": "N2"}
    data_frame.set_filter(filter_text)
    data_frame.expect_cell("3", row=0, col=1)

    # respect filtering even after edits when filters have been applied
    data_frame.set_cell("3", row=0, col=1, finish_key="Enter")
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
    filter_num_range: list[ColumnFilter] = [
        {"col": 6, "value": "N2"},
        {"col": 1, "value": (40, 50)},
    ]
    data_frame.set_filter(filter_num_range)
    data_frame.expect_cell("40", row=0, col=1)

    # Editing a cell in the first row and hitting `shift+enter` should not submit the change and stay editing the current cell
    data_frame.expect_cell("N25A2", row=0, col=6)
    data_frame.set_cell("NAAAAA", row=0, col=6, finish_key="Shift+Enter")
    data_frame.expect_cell("N25A2", row=0, col=6)
    data_frame.set_cell("NBBBBB", row=0, col=6, finish_key="Escape")
    data_frame.expect_cell("N25A2", row=0, col=6)

    # Editing a cell in the last row and hitting `enter` should not submit the change and stay editing the current cell
    # data_frame.set_column_filter(7, text="No")
    # Test scrolling to last row
    data_frame.set_cell("NAAAAA", row=7, col=6, finish_key="Enter")
    data_frame.expect_cell("N29A2", row=7, col=6)
    data_frame.set_cell("NAAAAA", row=7, col=6, finish_key="Escape")
    data_frame.expect_cell("N29A2", row=7, col=6)

    # Test scrolling up to top
    data_frame.expect_cell("N25A2", row=0, col=6)
