from __future__ import annotations

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
            "style": {"color": "darkorange", "font-weight": "bold"},
            "class": "everywhere",
        },
        {
            "location": "body",
            "rows": [1, 2],
            "cols": "Species",
            "class": "species",
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
        df: controller.OutputDataFrame,
        styles: list[dict[str, Jsonifiable]],
    ):
        def class_for_cell(row: int, col: int) -> list[str]:
            classes: list[str] = []
            for style in styles:
                if isinstance(style["rows"], list):
                    if row not in style["rows"]:
                        continue
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
                    shiny_expect.expect_attribute_to_have_value(cell_loc, "class", None)
                else:
                    for ex_class in classes:
                        assert isinstance(ex_class, str)

                        shiny_expect.expect_to_have_class(cell_loc, ex_class)

    expect_styles(
        fn_styles,
    )
    expect_styles(list_styles, every_styles_with_style)

    fn_styles.save_cell("new value", row=0, col=0, save_key="Enter")
    expect_styles(fn_styles, [styles[0], styles[1]])

    fn_styles.save_cell("new value2", row=0, col=0, save_key="Enter")
    expect_styles(fn_styles, [styles[0], styles[1], styles[2]])

    fn_styles.save_cell("new value3", row=0, col=0, save_key="Enter")
    expect_styles(fn_styles, [styles[0], styles[1], styles[2], styles[3]])

    fn_styles.save_cell("new value4", row=0, col=0, save_key="Enter")
    expect_styles(fn_styles, [styles[0]])
