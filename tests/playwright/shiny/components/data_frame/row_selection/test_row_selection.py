from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def expect_row_selection(page: Page, prefix_main: str, prefix_secondary: str):
    # TODO: Karan, add Dataframe helpers methods for selected_rows

    main_txt_rows = controller.OutputTextVerbatim(page, f"{prefix_main}selected_rows")
    other_txt_rows = controller.OutputTextVerbatim(
        page, f"{prefix_secondary}selected_rows"
    )

    main_selected_row_count = controller.OutputTextVerbatim(
        page, f"{prefix_main}selected_row_count"
    )
    other_selected_row_count = controller.OutputTextVerbatim(
        page, f"{prefix_secondary}selected_row_count"
    )

    main_grid_row_count = controller.OutputTextVerbatim(
        page, f"{prefix_main}grid_row_count"
    )
    other_grid_row_count = controller.OutputTextVerbatim(
        page, f"{prefix_secondary}grid_row_count"
    )

    main_select_btn = controller.InputActionButton(page, f"{prefix_main}select")
    main_clear_btn = controller.InputActionButton(page, f"{prefix_main}clear")

    main_txt_rows.expect_value("()")
    other_txt_rows.expect_value("()")
    main_selected_row_count.expect_value("0")
    other_selected_row_count.expect_value("0")
    main_grid_row_count.expect_value("344")
    other_grid_row_count.expect_value("344")

    main_select_btn.click()
    main_txt_rows.expect_value("(1, 3, 5)")
    other_txt_rows.expect_value("()")
    main_selected_row_count.expect_value("3")
    other_selected_row_count.expect_value("0")
    main_grid_row_count.expect_value("344")
    other_grid_row_count.expect_value("344")

    main_clear_btn.click()

    main_txt_rows.expect_value("()")
    other_txt_rows.expect_value("()")
    main_selected_row_count.expect_value("0")
    other_selected_row_count.expect_value("0")
    main_grid_row_count.expect_value("344")
    other_grid_row_count.expect_value("344")


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    expect_row_selection(page, "", "pandas-")
    expect_row_selection(page, "pandas-", "")

    expect_row_selection(page, "", "polars-")
    expect_row_selection(page, "polars-", "")
