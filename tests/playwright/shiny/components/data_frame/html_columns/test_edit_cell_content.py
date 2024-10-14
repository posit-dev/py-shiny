import pytest
from playwright.sync_api import Page
from utils.deploy_utils import skip_if_not_chrome

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_if_not_chrome
@pytest.mark.parametrize("df_type", ["pandas", "polars"])
def test_edit_cell_content_is_not_null(
    page: Page, local_app: ShinyAppProc, df_type: str
) -> None:
    page.goto(local_app.url)

    data_frame = controller.OutputDataFrame(page, f"{df_type}_df")

    tab = controller.NavsetCardUnderline(page, "tab")
    tab.set(df_type)

    data_frame.expect_cell("", row=0, col=14)
    empty_cell = data_frame.cell_locator(row=0, col=14)
    empty_cell.dblclick()
    textarea = empty_cell.locator("textarea")
    textarea.wait_for()
    cur_value = textarea.input_value()
    assert cur_value == ""
