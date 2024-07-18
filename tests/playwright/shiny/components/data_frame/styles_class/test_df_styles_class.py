from __future__ import annotations

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.playwright import expect as shiny_expect
from shiny.run import ShinyAppProc
from shiny.types import Jsonifiable


def test_validate_column_labels(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    pd_list_styles = controller.OutputDataFrame(page, "pd_list_styles")
    pl_list_styles = controller.OutputDataFrame(page, "pl_list_styles")

    styles: list[dict[str, Jsonifiable]] = [
        {
            "style": {"color": "darkorange", "font-weight": "bold"},
            "class": "everywhere",
        },
        {
            "rows": [1, 2],
            "cols": [2],  # "Species",
            "class": "species",
        },
    ]

    def expect_styles(
        df: controller.OutputDataFrame,
        styles: list[dict[str, Jsonifiable]],
    ):
        def class_for_cell(row: int, col: int) -> list[str]:
            classes: list[str] = []
            for style in styles:
                if "rows" in style:
                    if isinstance(style["rows"], list):
                        if row not in style["rows"]:
                            continue
                if "cols" in style:
                    if isinstance(style["cols"], list):
                        if col not in style["cols"]:
                            continue
                assert isinstance(style["class"], str)
                classes.append(style["class"])
            return classes

        for row in range(0, 5):
            for col in range(0, 6):
                cell_loc = df.cell_locator(row=row, col=col)
                classes = class_for_cell(row, col)

                if len(classes) == 0:
                    shiny_expect.expect_not_to_have_attribute(cell_loc, "class")
                else:
                    for ex_class in classes:
                        assert isinstance(ex_class, str)

                        shiny_expect.expect_to_have_class(cell_loc, ex_class)

    expect_styles(pd_list_styles, styles)
    expect_styles(pl_list_styles, styles)
