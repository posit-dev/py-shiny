from playwright.sync_api import Page

from shiny.playwright.controls import OutputDataFrame
from shiny.run import ShinyAppProc


def test_validate_data_edit_mode(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    data_frame = OutputDataFrame(page, "penguins_df")
    data_frame.save_cell("Study0708_edited", row=1, col=1, save_key="Enter")
    data_frame.expect_class_state("saving", row=1, col=1)
    data_frame.expect_class_state("editing", row=2, col=1)
