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
    )

    data_frame.expect_cell("PAL0708", row=1, col=1)
    data_frame.expect_n_col(17)
    data_frame.expect_class_state("ready", row=1, col=1)
    data_frame.expect_column_label(["Species"], col=3)
    data_frame.edit_cell("Study0708_edited", row=1, col=1)
    data_frame.expect_class_state("editing", row=1, col=1)
    data_frame.save_cell("Study0708_edited", row=1, col=1, save_key="Enter")
    # data_frame.expect_class_state("saving", row=1, col=1)
    data_frame.expect_class_state("editing", row=2, col=1)
    data_frame.expect_class_state("success", row=1, col=1)
    data_frame.expect_cell("Study0708_edited", row=1, col=1)

    data_frame.expect_cell("Torgersen", row=1, col=5)
    data_frame.save_cell("Stonington", row=1, col=5, save_key="Enter")
    data_frame.expect_class_state("failure", row=1, col=5)
    data_frame.expect_cell_title(
        "Penguin island should be one of 'Torgersen', 'Biscoe', 'Dream'", row=1, col=5
    )
    data_frame.expect_cell("Torgersen", row=1, col=5)

    data_frame.expect_cell("39.5", row=2, col=10)
    data_frame.save_cell("Stonington", row=2, col=10, save_key="Shift+Enter")
    data_frame.expect_class_state("editing", row=1, col=10)
