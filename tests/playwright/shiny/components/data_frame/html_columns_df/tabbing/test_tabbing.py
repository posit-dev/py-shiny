import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@pytest.mark.parametrize("tab_name", ["pandas", "polars"])
def test_validate_html_columns(
    page: Page,
    local_app: ShinyAppProc,
    tab_name: str,
) -> None:
    page.goto(local_app.url)

    controller.NavsetCardUnderline(page, "tab").set(tab_name)

    data_frame = controller.OutputDataFrame(page, f"{tab_name}_iris")
    # Data frame with html content in the first two columns; Edit a cell in the third column and try to hit `shift + tab`. It should not submit the edit in the current cell and stay at the current cell (not moving to the second or first column)
    data_frame.expect_cell("1.4", row=0, col=2)
    data_frame.set_cell("152", row=0, col=2, finish_key="Shift+Tab")
    data_frame.expect_cell("1.4", row=0, col=2)
    data_frame.expect_cell_class("cell-edit-editing", row=0, col=2)

    # Data frame with html content in the last two columns; Edit a cell in the third from last column and try to hit `tab`. It should not submit the edit in the current cell and stay at the current cell (not moving to the last two columns)
    data_frame.expect_cell("1.4", row=0, col=2)
    data_frame.set_cell("152", row=0, col=2, finish_key="Tab")
    data_frame.expect_cell("1.4", row=0, col=2)
    data_frame.expect_cell_class("cell-edit-editing", row=0, col=2)
