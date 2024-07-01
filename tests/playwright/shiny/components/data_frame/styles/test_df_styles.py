from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.playwright import expect as shiny_expect
from shiny.run import ShinyAppProc
from shiny.types import Jsonifiable


def test_validate_column_labels(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    fn_styles = controller.OutputDataFrame(page, "fn_styles")
    list_styles = controller.OutputDataFrame(page, "list_styles")

    styles: list[dict[str, Jsonifiable]] = [
        {
            "location": "body",
            "rows": [1, 2],
            "cols": [2],  # "Species",
            "style": {
                "background-color": "purple",
                "border-color": "green",
                "border-style": "dashed",
            },
        },
        {
            "location": "body",
            "rows": [2],
            "cols": [3],  # "Region",
            "style": {"background-color": "yellow"},
        },
        {
            "location": "body",
            "rows": None,
            "cols": [4],  # "Island",
            "style": {"background-color": "red"},
        },
    ]

    def expect_styles(
        df: controller.OutputDataFrame, styles: list[dict[str, Jsonifiable]]
    ):
        def style_for_cell(row: int, col: int) -> dict[str, Jsonifiable] | None:
            for style in styles:
                if isinstance(style["rows"], list):
                    if row not in style["rows"]:
                        continue
                if isinstance(style["cols"], list):
                    if col not in style["cols"]:
                        continue
                assert isinstance(style["style"], dict)
                return style["style"]
            return None

        for row in range(0, 5):
            for col in range(0, 6):
                cell_loc = df.cell_locator(row=row, col=col)
                ex_cell_style = style_for_cell(row, col)

                if ex_cell_style is None:

                    shiny_expect.expect_to_have_style(
                        cell_loc, "background-color", None
                    )
                else:
                    assert isinstance(ex_cell_style, dict)
                    assert "background-color" in ex_cell_style
                    assert isinstance(ex_cell_style["background-color"], str)

                    shiny_expect.expect_to_have_style(
                        cell_loc, "background-color", ex_cell_style["background-color"]
                    )

    expect_styles(fn_styles, [styles[0]])
    expect_styles(list_styles, styles)

    fn_styles.edit_cell("new value", row=0, col=0)
    expect_styles(fn_styles, [styles[0], styles[1]])

    fn_styles.edit_cell("new value2", row=0, col=0)
    expect_styles(fn_styles, [])
