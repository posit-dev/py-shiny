from __future__ import annotations

import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.playwright import expect as shiny_expect
from shiny.run import ShinyAppProc
from shiny.types import Jsonifiable


@pytest.mark.parametrize("tab_name", ["pandas", "polars"])
def test_validate_column_labels(
    page: Page, local_app: ShinyAppProc, tab_name: str
) -> None:
    page.goto(local_app.url)

    controller.NavsetUnderline(page, "tab").set(tab_name)

    fn_styles = controller.OutputDataFrame(page, f"{tab_name}-fn_styles")
    list_styles = controller.OutputDataFrame(page, f"{tab_name}-list_styles")

    styles: list[dict[str, Jsonifiable]] = [
        {
            "rows": [1, 2],
            "cols": [2],  # "Species",
            "style": {
                "background-color": "purple",
                "border-color": "green",
                "border-style": "dashed",
            },
        },
        {
            "rows": [2],
            "cols": [3],  # "Region",
            "style": {"background-color": "yellow"},
        },
        {
            "rows": None,
            "cols": [4],  # "Island",
            "style": {"background-color": "red"},
        },
        {
            "rows": [1],
            "cols": [4, 5],  # "Island", "Stage",
            "style": {"background-color": "green"},
        },
    ]

    every_styles: dict[str, Jsonifiable] = {
        "location": "body",
        "rows": None,
        "cols": None,
        "style": {"background-color": "lightblue", "color": "darkorange"},
    }
    every_styles_with_style: list[dict[str, Jsonifiable]] = [every_styles]
    for style in styles:
        every_styles_with_style.append(style)

    def expect_styles(
        df: controller.OutputDataFrame, styles: list[dict[str, Jsonifiable]]
    ):
        def style_for_cell(row: int, col: int) -> dict[str, Jsonifiable] | None:
            last_val: dict[str, Jsonifiable] | None = None
            for style in styles:
                if isinstance(style["rows"], list):
                    if row not in style["rows"]:
                        continue
                if isinstance(style["cols"], list):
                    if col not in style["cols"]:
                        continue
                assert isinstance(style["style"], dict)
                last_val = style["style"]
            return last_val

        for row in range(0, 5):
            for col in range(0, 6):
                cell_loc = df.cell_locator(row=row, col=col)
                ex_cell_style = style_for_cell(row, col)

                if ex_cell_style is None:

                    shiny_expect.expect_not_to_have_style(cell_loc, "background-color")
                else:
                    assert isinstance(ex_cell_style, dict)
                    assert "background-color" in ex_cell_style
                    assert isinstance(ex_cell_style["background-color"], str)

                    shiny_expect.expect_to_have_style(
                        cell_loc, "background-color", ex_cell_style["background-color"]
                    )

    expect_styles(fn_styles, [styles[0]])
    expect_styles(list_styles, every_styles_with_style)

    fn_styles.set_cell("new value", row=0, col=0)
    expect_styles(fn_styles, [styles[0], styles[1]])

    fn_styles.set_cell("new value2", row=1, col=0)
    expect_styles(fn_styles, [styles[0], styles[1], styles[2]])

    fn_styles.set_cell("new value3", row=2, col=0)
    expect_styles(fn_styles, [styles[0], styles[1], styles[2], styles[3]])

    fn_styles.set_cell("new value4", row=3, col=0)
    expect_styles(fn_styles, [styles[0]])
