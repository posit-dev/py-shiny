from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_validate_column_labels(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    w_filters = controller.OutputDataFrame(page, "w_filters")
    wo_filters = controller.OutputDataFrame(page, "wo_filters")

    ex_labels = [
        "Sample Number",
        "Species",
        "Region",
    ]

    w_filters.expect_column_labels(ex_labels)
    wo_filters.expect_column_labels(ex_labels)
