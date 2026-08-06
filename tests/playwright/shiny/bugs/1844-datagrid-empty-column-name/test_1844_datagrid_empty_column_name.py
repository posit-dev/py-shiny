from __future__ import annotations

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_datagrid_empty_column_name(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    df = controller.OutputDataFrame(page, "df1")
    sort_value = controller.OutputCode(page, "sort_value")
    filter_value = controller.OutputCode(page, "filter_value")
    data_view_rows = controller.OutputCode(page, "data_view_rows")

    # The grid renders, empty column name included
    df.expect_ncol(2)
    df.expect_nrow(3)
    df.expect_column_labels(["", "num"])
    df.expect_cell("c", row=0, col=0)
    df.expect_cell("3", row=0, col=1)
    data_view_rows.expect_value("rows: (0, 1, 2)")

    # Client -> server: sorting on the empty-named column reports its index
    df.set_sort(0)
    sort_value.expect_value("sort: ({'col': 0, 'desc': False},)")
    data_view_rows.expect_value("rows: (1, 2, 0)")
    df.expect_cell("a", row=0, col=0)

    df.set_sort(None)
    sort_value.expect_value("sort: ()")
    data_view_rows.expect_value("rows: (0, 1, 2)")

    # Server -> client: `.update_sort()` on the empty-named column is applied
    controller.InputActionButton(page, "update_sort").click()
    sort_value.expect_value("sort: ({'col': 0, 'desc': True},)")
    data_view_rows.expect_value("rows: (0, 2, 1)")
    df.expect_cell("c", row=0, col=0)

    df.set_sort(None)

    # Client -> server: filtering on the empty-named column reports its index
    df.set_filter({"col": 0, "value": "b"})
    filter_value.expect_value("filter: ({'col': 0, 'value': 'b'},)")
    df.expect_nrow(1)
    data_view_rows.expect_value("rows: (2,)")

    df.set_filter(None)
    filter_value.expect_value("filter: ()")
    df.expect_nrow(3)

    # Server -> client: `.update_filter()` on the empty-named column is applied
    controller.InputActionButton(page, "update_filter").click()
    filter_value.expect_value("filter: ({'col': 0, 'value': 'b'},)")
    df.expect_nrow(1)
    data_view_rows.expect_value("rows: (2,)")
