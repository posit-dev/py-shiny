from shiny.test import Page, ShinyAppProc
from shiny.test._controls import OutputDataFrame


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

    data_frame.expect_cell("PAL0708", row=0, col=0)
    data_frame.expect_n_col(17)
    data_frame.expect_class_state("ready", row=0, col=0)
    data_frame.expect_column_label(["Species"], col=3)
    data_frame.edit_cell("Study0708_edited", row=0, col=0)
    data_frame.expect_class_state("editing", row=0, col=0)
    data_frame.save_cell("Study0708_edited", row=0, col=0, save_key="Enter")
    # data_frame.expect_class_state("saving", row=0, col=0)
    data_frame.expect_class_state("editing", row=1, col=0)
    data_frame.expect_class_state("success", row=0, col=0)
    data_frame.expect_cell("Study0708_edited", row=0, col=0)

    data_frame.expect_cell("Torgersen", row=0, col=4)
    data_frame.save_cell("Stonington", row=0, col=4, save_key="Enter")
    data_frame.expect_class_state("failure", row=0, col=4)
    data_frame.expect_cell_title(
        "Penguin island should be one of 'Torgersen', 'Biscoe', 'Dream'", row=0, col=4
    )
    data_frame.expect_cell("Torgersen", row=0, col=4)

    data_frame.expect_cell("39.5", row=1, col=9)
    data_frame.save_cell("Stonington", row=1, col=9, save_key="Shift+Enter")
    data_frame.expect_class_state("editing", row=0, col=9)
