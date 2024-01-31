from conftest import ShinyAppProc, create_doc_example_core_fixture
from controls import OutputTable
from playwright.sync_api import Page

app = create_doc_example_core_fixture("output_table")


def test_output_plot_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    table = OutputTable(page, "result")

    table.expect_n_col(11)
    table.expect_n_row(32)

    table.expect_cell("93", 3, 4)
    table.expect_cell("2.875", 2, 6)

    table.expect_column_labels(
        [
            "mpg",
            "cyl",
            "disp",
            "hp",
            "drat",
            "wt",
            "qsec",
            "vs",
            "am",
            "gear",
            "carb",
        ]
    )

    table.expect_column_text(
        2,
        [
            "6",
            "6",
            "4",
            "6",
            "8",
            "6",
            "8",
            "4",
            "4",
            "6",
            "6",
            "8",
            "8",
            "8",
            "8",
            "8",
            "8",
            "4",
            "4",
            "4",
            "4",
            "8",
            "8",
            "8",
            "8",
            "4",
            "4",
            "4",
            "8",
            "6",
            "8",
            "4",
        ],
    )
