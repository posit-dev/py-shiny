from conftest import ShinyAppProc
from controls import OutputDataFrame, OutputTextVerbatim
from playwright.sync_api import Page


def test_validate_html_columns(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    data_frame = OutputDataFrame(page, "testing-penguins_df")

    sort = OutputTextVerbatim(page, "testing-sort")
    filter = OutputTextVerbatim(page, "testing-filter")
    rows = OutputTextVerbatim(page, "testing-rows")
    selected_rows = OutputTextVerbatim(page, "testing-selected_rows")

    sort.expect_value("()")
    filter.expect_value("()")
    rows.expect_value("(0, 1, 2, 3, 4)")
    selected_rows.expect_value("")

    data_frame.set_column_sort(col=2)
    data_frame.set_column_sort(col=2)
    sort.expect_value("({'col': 2, 'desc': True},)")
    filter.expect_value("()")
    rows.expect_value("(2, 3, 4, 0, 1)")
    selected_rows.expect_value("")
    data_frame.select_rows([1, 3])
    selected_rows.expect_value("(3, 0)")
    data_frame.select_rows([1, 3])  # unselect the rows
    selected_rows.expect_value("")

    data_frame.set_column_filter(1, text="A2")
    sort.expect_value("({'col': 2, 'desc': True},)")

    data_frame.set_column_filter(0, text=["2", ""])
    filter.expect_value("({'col': 1, 'value': 'A2'}, {'col': 0, 'value': (2, None)})")

    rows.expect_value("(3, 1)")
    selected_rows.expect_value("")
    data_frame.select_rows([0])
    rows.expect_value("(3, 1)")
    selected_rows.expect_value("(3,)")
