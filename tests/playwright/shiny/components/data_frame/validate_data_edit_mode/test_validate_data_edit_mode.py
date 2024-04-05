from conftest import ShinyAppProc
from controls import OutputDataFrame
from playwright.sync_api import Page


def test_validate_data_edit_mode(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    data_frame = OutputDataFrame(page, "penguins_df")
    data_frame.expect_column_labels(
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
        ],
        edit=True,
    )

    data_frame.expect_cell("PAL0708", 1, 1)
    data_frame.expect_n_col(17, edit=True)
    data_frame.expect_column_text(3, ["Species"])
    data_frame.set_cell_value("Study0708_edited", 1, 1)
    data_frame.expect_cell_class(1, 1, "cell-edit-editing")
    page.keyboard.press("Enter")
    data_frame.expect_cell_class(2, 1, "cell-edit-editing")
    data_frame.expect_cell_class(1, 1, "cell-edit-success")
    data_frame.expect_cell("Study0708_edited", 1, 1)

    data_frame.expect_cell("Torgersen", 1, 5)
    data_frame.set_cell_value("Stonington", 1, 5)
    data_frame.expect_cell_class(1, 5, "cell-edit-editing")
    page.keyboard.press("Enter")
    data_frame.expect_cell_class(1, 5, "cell-edit-failure")
    data_frame.expect_cell_validation_message(
        1, 5, "Penguin island should be one of 'Torgersen', 'Biscoe', 'Dream'"
    )
    data_frame.expect_cell("Torgersen", 1, 5)

    data_frame.expect_cell("39.5", 2, 10)
    data_frame.set_cell_value("Stonington", 2, 10)
    data_frame.expect_cell_class(2, 10, "cell-edit-editing")
    page.keyboard.press("Shift+Enter")
    data_frame.expect_cell_class(1, 10, "cell-edit-editing")
