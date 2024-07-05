from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.render._data_frame import ColumnFilterNumber, ColumnFilterStr, ColumnSort
from shiny.run import ShinyAppProc


def test_validate_html_columns(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    data_frame = controller.OutputDataFrame(page, "testing-penguins_df")

    sort = controller.OutputTextVerbatim(page, "testing-sort")
    filter = controller.OutputTextVerbatim(page, "testing-filter")
    rows = controller.OutputTextVerbatim(page, "testing-rows")
    selected_rows = controller.OutputTextVerbatim(page, "testing-selected_rows")

    sort.expect_value("()")
    filter.expect_value("()")
    rows.expect_value("(0, 1, 2, 3, 4)")
    selected_rows.expect_value("()")
    col: ColumnSort = {
        "col": 2,
        "desc": False,
    }
    data_frame.set_sort(col)
    sort.expect_value("({'col': 2, 'desc': True},)")
    filter.expect_value("()")
    rows.expect_value("(2, 3, 4, 0, 1)")
    selected_rows.expect_value("()")
    data_frame.select_rows([1, 3])
    selected_rows.expect_value("(3, 0)")
    data_frame.select_rows([1, 3])  # unselect the rows
    selected_rows.expect_value("()")

    filter_text: ColumnFilterStr = {"col": 1, "value": "A2"}
    data_frame.set_filter(filter_text)
    sort.expect_value("({'col': 2, 'desc': True},)")

    filter_criteria_num: ColumnFilterNumber = {"col": 1, "value": (2, None)}
    data_frame.set_filter(filter_criteria_num)
    filter.expect_value("({'col': 1, 'value': 'A2'}, {'col': 0, 'value': (2, None)})")

    rows.expect_value("(3, 1)")
    selected_rows.expect_value("()")
    data_frame.select_rows([0])
    rows.expect_value("(3, 1)")
    selected_rows.expect_value("(3,)")
