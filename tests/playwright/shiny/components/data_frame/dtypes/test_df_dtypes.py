from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_dataframe_methods(page: Page, local_app: ShinyAppProc) -> None:

    page.goto(local_app.url)

    df_html = controller.OutputDataFrame(page, "df_html")

    df_html.expect_nrow(2)
    df_html.expect_ncol(12)

    df_html.expect_column_labels(
        [
            "num",
            "chr",
            "cat",
            "bool",
            "date",
            "datetime",
            "duration",
            "html",
            "html_str",
            "struct",
            "arr",
            "object",
        ]
    )

    df_html.expect_cell("1", row=0, col=0)
    df_html.expect_cell("2", row=1, col=0)

    df_html.expect_cell("a", row=0, col=1)
    df_html.expect_cell("b", row=1, col=1)

    df_html.expect_cell("c", row=0, col=2)
    df_html.expect_cell("d", row=1, col=2)

    df_html.expect_cell("true", row=0, col=3)
    df_html.expect_cell("false", row=1, col=3)

    df_html.expect_cell("2000-01-02", row=0, col=4)
    df_html.expect_cell("2000-01-02", row=1, col=4)

    df_html.expect_cell("2000-01-02 00:00:00", row=0, col=5)
    df_html.expect_cell("2000-01-02 00:00:00", row=1, col=5)

    df_html.expect_cell("7 days 00:00:00", row=0, col=6)
    df_html.expect_cell("7 days 00:00:00", row=1, col=6)

    df_html.expect_cell("bolded content", row=0, col=7)
    df_html.expect_cell("bolded content", row=1, col=7)
    # Verify that is cell has a **strong** tag and isn't a string
    expect(df_html.cell_locator(row=0, col=7).locator("strong")).to_have_text(
        "bolded content"
    )

    df_html.expect_cell("bolded string", row=0, col=8)
    df_html.expect_cell("bolded string", row=1, col=8)
    # Verify that is cell has a **strong** tag and isn't a string
    expect(df_html.cell_locator(row=0, col=8).locator("strong")).to_have_text(
        "bolded string"
    )

    df_html.expect_cell('{"x":1}', row=0, col=9)
    df_html.expect_cell('{"x":2}', row=1, col=9)

    df_html.expect_cell("[1,2]", row=0, col=10)
    df_html.expect_cell("[3,4]", row=1, col=10)

    df_html.expect_cell("<C object>", row=0, col=11)
    df_html.expect_cell('{"y":2}', row=1, col=11)
