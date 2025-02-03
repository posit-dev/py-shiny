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
