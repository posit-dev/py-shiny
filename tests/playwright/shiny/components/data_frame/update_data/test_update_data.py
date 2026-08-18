from __future__ import annotations

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_update_data(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    df = controller.OutputDataFrame(page, "df")
    df_selected = controller.OutputDataFrame(page, "df_selected")
    shift_btn = controller.InputActionButton(page, "shift_btn")
    different_btn = controller.InputActionButton(page, "different_btn")

    df.expect_nrow(344)
    df.expect_ncol(2)
    df_selected.expect_column_labels(["studyName", "Sample Number"])

    df_selected.expect_nrow(0)
    df_selected.expect_ncol(2)
    df_selected.expect_column_labels(["studyName", "Sample Number"])

    df.select_rows([1])
    df_selected.expect_nrow(1)
    df_selected.expect_cell("2", row=0, col=1)

    # Shift data
    shift_btn.click()
    df.expect_nrow(2)
    df.expect_ncol(2)
    df.expect_column_labels(["studyName", "Sample Number"])
    df.expect_selected_rows([1])
    df.expect_cell("3", row=0, col=1)
    df.expect_cell("4", row=1, col=1)
    df_selected.expect_nrow(1)
    df_selected.expect_ncol(2)
    df_selected.expect_cell("4", row=0, col=1)

    # Change data set
    different_btn.click()
    df.expect_nrow(26)
    df.expect_ncol(2)
    df.expect_column_labels(["Letter", "Negative index"])
    df.expect_selected_rows([1])

    df_selected.expect_nrow(1)
    df_selected.expect_ncol(2)
    df_selected.expect_cell("b", row=0, col=0)
    df_selected.expect_cell("-2", row=0, col=1)

    # Change data set again
    different_btn.click()
    df.expect_nrow(344)
    df.expect_ncol(17)
    df.expect_column_labels(
        [
            "studyName",
            "Sample Number",
            "Species",
            "Region",
            "Island",
            "Stage",
            "Individual ID",
            "Clutch Completion",
            "Date Egg",
            "Culmen Length (mm)",
            "Culmen Depth (mm)",
            "Flipper Length (mm)",
            "Body Mass (g)",
            "Sex",
            "Delta 15 N (o/oo)",
            "Delta 13 C (o/oo)",
            "Comments",
        ]
    )
    df.expect_selected_rows([1])


def test_update_data_keeps_sort_and_filter_on_named_column(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    df = controller.OutputDataFrame(page, "df")
    sort_value = controller.OutputCode(page, "sort_value")
    filter_value = controller.OutputCode(page, "filter_value")
    reorder_btn = controller.InputActionButton(page, "reorder_btn")
    different_btn = controller.InputActionButton(page, "different_btn")

    df.expect_column_labels(["studyName", "Sample Number"])

    # Sort and filter the first column, "studyName"
    df.set_sort(0)
    sort_value.expect_value("sort: ({'col': 0, 'desc': False},)")
    df.set_filter({"col": 0, "value": "PAL0708"})
    filter_value.expect_value("filter: ({'col': 0, 'value': 'PAL0708'},)")
    df.expect_nrow(110)

    # `update_data()` with the same columns in the opposite order: the sort and
    # the filter stay on "studyName", which is now at index 1
    reorder_btn.click()
    df.expect_column_labels(["Sample Number", "studyName"])
    sort_value.expect_value("sort: ({'col': 1, 'desc': False},)")
    filter_value.expect_value("filter: ({'col': 1, 'value': 'PAL0708'},)")
    df.expect_nrow(110)
    df.expect_cell("PAL0708", row=0, col=1)

    # `update_data()` with columns that share no name with the old ones: the
    # sort and the filter are dropped rather than applied to another column
    different_btn.click()
    df.expect_column_labels(["Letter", "Negative index"])
    sort_value.expect_value("sort: ()")
    filter_value.expect_value("filter: ()")
    df.expect_nrow(26)
