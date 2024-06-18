from playwright.sync_api import Page

from shiny.playwright.controls import OutputDataFrame
from shiny.run import ShinyAppProc


def test_validate_column_labels(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    w_filters = OutputDataFrame(page, "w_filters")
    wo_filters = OutputDataFrame(page, "wo_filters")

    ex_labels = [
        "Sample Number",
        "Species",
        "Region",
    ]

    w_filters.expect_column_labels(ex_labels)
    wo_filters.expect_column_labels(ex_labels)
