import re

import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.render._data_frame_utils._types import (
    ColumnFilterNumber,
    ColumnFilterStr,
    ColumnSort,
)
from shiny.run import ShinyAppProc


@pytest.mark.parametrize("tab_name", ["pandas", "polars"])
def test_validate_html_columns(
    page: Page,
    local_app: ShinyAppProc,
    tab_name: str,
) -> None:
    page.goto(local_app.url)

    data_frame = controller.OutputDataFrame(page, f"{tab_name}-penguins_df")
    tab = controller.NavsetUnderline(page, "tab")
    tab.set(tab_name)

    controller.OutputTextVerbatim(page, f"{tab_name}-df_type").expect_value(
        re.compile(tab_name)
    )

    sort = controller.OutputTextVerbatim(page, f"{tab_name}-sort")
    filter = controller.OutputTextVerbatim(page, f"{tab_name}-filter")
    rows = controller.OutputTextVerbatim(page, f"{tab_name}-rows")
    selected_rows = controller.OutputTextVerbatim(page, f"{tab_name}-selected_rows")

    sort.expect_value("()")
    filter.expect_value("()")
    rows.expect_value("(0, 1, 2, 3, 4)")
    selected_rows.expect_value("()")
    col: ColumnSort = {
        "col": 2,
        "desc": True,
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

    filter_criteria_num: ColumnFilterNumber = {"col": 0, "value": [2, None]}
    data_frame.set_filter([filter_criteria_num])
    filter.expect_value("({'col': 0, 'value': (2, None)},)")
    data_frame.set_filter([filter_criteria_num, filter_text])
    filter.expect_value("({'col': 0, 'value': (2, None)}, {'col': 1, 'value': 'A2'})")

    rows.expect_value("(3, 1)")
    selected_rows.expect_value("()")
    data_frame.select_rows([0])
    rows.expect_value("(3, 1)")
    selected_rows.expect_value("(3,)")
