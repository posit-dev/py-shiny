from conftest import ShinyAppProc
from controls import OutputDataFrame
from playwright.sync_api import Page


def test_validate_data_edit_mode(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    data_frame = OutputDataFrame(page, "penguins_df")

    # Expect column labels to be present and editable
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

    # Expect specific cell value at a given row and column
    data_frame.expect_cell("PAL0708", 1, 1)

    # Expect a specific number of columns when dataframe allows editing
    data_frame.expect_n_col(17, edit=True)

    # Expect specific text in a column
    data_frame.expect_column_text(3, ["Species"])

    # Set a new value for a specific cell and expect it to be updated
    data_frame.set_cell_value("Study0708_edited", 1, 1)
    data_frame.expect_cell("Study0708_edited", 1, 1)

    # Set a new value for a specific cell and expect it to fail validation
    data_frame.set_cell_value("Stonington", 1, 5)
    data_frame.expect_cell_validation_message(
        1, 5, "Penguin island should be one of 'Torgersen', 'Biscoe', 'Dream'"
    )
    data_frame.expect_cell("Torgersen", 1, 5)
    data_frame.set_cell_value("Stonington", 2, 10)
    data_frame.expect_cell_class(1, 10, "cell-edit-editing")
