import pytest
from playwright.sync_api import Page
from utils.deploy_utils import reruns, reruns_delay, skip_if_not_chrome

from shiny.playwright import controller
from shiny.run import ShinyAppProc


# Edit mode becomes flaky near end of test on CI on webkit.
@skip_if_not_chrome
@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
def test_validate_row_selection_in_edit_mode(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.set_viewport_size({"width": 1920 * 2, "height": 1080 * 2})
    page.goto(local_app.url)

    # Select (and verify) a row. Edit a cell content in that row.
    # Verify the row is not focused. Hit escape key. Verify the cell value is not updated.
    # Verify the row is focused. Hit escape key again.
    # Verify the row is not focused. (Possibly verify the container div is focused?)
    data_frame = controller.OutputDataFrame(page, "penguins_df")

    data_frame.expect_cell("N1A2", row=1, col=6)
    data_frame._edit_cell_no_save("N2A2", row=1, col=6)
    data_frame._expect_row_focus_state(False, row=1)
    data_frame.expect_class_state("editing", row=1, col=6)
    data_frame.expect_selected_num_rows(1)
    data_frame.expect_selected_rows([1])
    data_frame.set_cell("N3A2", row=1, col=6, finish_key="Escape")
    data_frame.expect_cell("N1A2", row=1, col=6)
    data_frame._expect_row_focus_state(True, row=1)
    page.keyboard.press("Escape")
    data_frame._expect_row_focus_state(False, row=1)

    # Enable rows selection and editable.
    # Select (and verify) a row. Edit a cell content in that row.
    # Click a cell in another row. Verify the new row is selected and focused.
    # Verify the old row is not selected. Verify the old row cell value was updated.
    data_frame.expect_cell("N1A2", row=1, col=6)
    data_frame._edit_cell_no_save("N2A2", row=1, col=6)
    data_frame._expect_row_focus_state(False, row=1)
    data_frame.expect_class_state("editing", row=1, col=6)
    data_frame.cell_locator(row=2, col=6).click()
    data_frame._expect_row_focus_state(True, row=2)
    data_frame._expect_row_focus_state(False, row=1)
    data_frame.expect_cell("N2A2", row=1, col=6)

    # Enable rows selection and editable.
    # Select (and verify) a row. Hit enter to edit the first cell in that row.
    # Hit escape key. Verify the same row is focused.
    # Scroll right and display an html column in the left part of the view.
    # Hit enter to edit the first visible non-html cell in that row.
    # Verify that cell is editing.
    data_frame.cell_locator(row=1, col=2).click()
    page.keyboard.press("Enter")
    data_frame._expect_row_focus_state(False, row=1)
    page.keyboard.press("Escape")
    data_frame._expect_row_focus_state(True, row=1)
    page.keyboard.press("Escape")
    data_frame._edit_cell_no_save("Temp value", row=1, col=16)
    page.keyboard.press("Escape")
    page.keyboard.press("Enter")
    data_frame.expect_class_state(
        "editing",
        row=1,
        col=0,
    )  # Stage column begins to be edited.

    # Click outside the table/Press Escape to exit row focus.
    # Tab to the column name, hit enter. Verify the table becomes sorted.
    # Tab to an HTML column name, hit enter. Verify the sort does not update.
    page.keyboard.press("Escape")
    page.keyboard.press("Escape")
    page.keyboard.press("Tab")
    page.keyboard.press("Tab")  # tab to sample number
    page.keyboard.press("Enter")
    data_frame.expect_cell("152", row=0, col=1)
    page.keyboard.press("Tab")
    page.keyboard.press("Enter")
    data_frame.expect_cell("Adelie Penguin (Pygoscelis adeliae)", row=0, col=2)
