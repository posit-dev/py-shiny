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


def test_datagrid_empty_column_name_middle_position(
    page: Page, local_app: ShinyAppProc
) -> None:
    # Same round trips as above, but with the empty column at index 1 rather
    # than index 0, so an implementation that only handled the first column
    # cannot pass.
    page.goto(local_app.url)

    df = controller.OutputDataFrame(page, "df2")
    sort_value = controller.OutputCode(page, "sort_value2")
    filter_value = controller.OutputCode(page, "filter_value2")
    data_view_rows = controller.OutputCode(page, "data_view_rows2")

    df.expect_ncol(3)
    df.expect_nrow(3)
    df.expect_column_labels(["chr", "", "num"])
    df.expect_cell("c", row=0, col=1)
    data_view_rows.expect_value("rows: (0, 1, 2)")

    # Client -> server: the reported index is 1, not 0
    df.set_sort(1)
    sort_value.expect_value("sort: ({'col': 1, 'desc': False},)")
    data_view_rows.expect_value("rows: (1, 2, 0)")
    df.expect_cell("a", row=0, col=1)

    df.set_sort(None)
    sort_value.expect_value("sort: ()")
    data_view_rows.expect_value("rows: (0, 1, 2)")

    # Server -> client: `.update_sort()` targets the empty column at index 1
    controller.InputActionButton(page, "update_sort").click()
    sort_value.expect_value("sort: ({'col': 1, 'desc': True},)")
    data_view_rows.expect_value("rows: (0, 2, 1)")
    df.expect_cell("c", row=0, col=1)

    df.set_sort(None)

    # Client -> server: filtering reports index 1
    df.set_filter({"col": 1, "value": "b"})
    filter_value.expect_value("filter: ({'col': 1, 'value': 'b'},)")
    df.expect_nrow(1)
    data_view_rows.expect_value("rows: (2,)")

    df.set_filter(None)
    filter_value.expect_value("filter: ()")
    df.expect_nrow(3)

    # Server -> client: `.update_filter()` targets the empty column at index 1
    controller.InputActionButton(page, "update_filter").click()
    filter_value.expect_value("filter: ({'col': 1, 'value': 'b'},)")
    df.expect_nrow(1)
    data_view_rows.expect_value("rows: (2,)")


def test_datagrid_update_sort_bare_index_uses_dtype(
    page: Page, local_app: ShinyAppProc
) -> None:
    # `.update_sort(<int>)` documents that `desc` follows the column dtype:
    # descending for number-like columns, ascending for everything else.
    page.goto(local_app.url)

    sort_value = controller.OutputCode(page, "sort_value")
    sort_value2 = controller.OutputCode(page, "sort_value2")

    controller.InputActionButton(page, "update_sort_int").click()

    # `df1` column 0 is the empty-named string column -> ascending
    sort_value.expect_value("sort: ({'col': 0, 'desc': False},)")
    # `df2` column 2 is `num` -> descending
    sort_value2.expect_value("sort: ({'col': 2, 'desc': True},)")


def test_datagrid_non_string_column_names(page: Page, local_app: ShinyAppProc) -> None:
    # pandas allows integer column names, which arrive at the client as JSON
    # numbers. Deriving TanStack column ids from them used to make the grid
    # throw while creating the column, blanking the whole output.
    page.goto(local_app.url)

    df = controller.OutputDataFrame(page, "df3")
    sort_value = controller.OutputCode(page, "sort_value3")
    data_view_rows = controller.OutputCode(page, "data_view_rows3")

    df.expect_ncol(3)
    df.expect_nrow(3)
    df.expect_column_labels(["0", "1", "1.5"])
    df.expect_cell("c", row=0, col=0)
    data_view_rows.expect_value("rows: (0, 1, 2)")

    df.set_sort(0)
    sort_value.expect_value("sort: ({'col': 0, 'desc': False},)")
    data_view_rows.expect_value("rows: (1, 2, 0)")
    df.expect_cell("a", row=0, col=0)
