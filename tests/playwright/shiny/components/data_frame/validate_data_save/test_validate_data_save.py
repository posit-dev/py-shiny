from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_validate_data_save(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    data_frame = controller.OutputDataFrame(page, "penguins_df")
    data_frame.set_cell("Study0708_edited", row=1, col=1, finish_key="Enter")
    data_frame.expect_class_state("saving", row=1, col=1)
    data_frame.expect_class_state("editing", row=2, col=1)
