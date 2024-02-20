from conftest import ShinyAppProc
from controls import InputActionButton, OutputTextVerbatim
from playwright.sync_api import Page


def expect_row_selection(page: Page, prefix_main: str, prefix_secondary: str):
    # TODO: Karan, add Dataframe helpers methods for selected_rows

    main_txt_rows = OutputTextVerbatim(page, f"{prefix_main}selected_rows")
    other_txt_rows = OutputTextVerbatim(page, f"{prefix_secondary}selected_rows")

    main_row_count = OutputTextVerbatim(page, f"{prefix_main}selected_row_count")
    other_row_count = OutputTextVerbatim(page, f"{prefix_secondary}selected_row_count")

    main_select_btn = InputActionButton(page, f"{prefix_main}select")
    main_clear_btn = InputActionButton(page, f"{prefix_main}clear")

    main_txt_rows.expect_value("()")
    other_txt_rows.expect_value("()")
    main_row_count.expect_value("grid: 0; selected: 0")
    other_row_count.expect_value("grid: 0; selected: 0")

    main_select_btn.click()
    main_txt_rows.expect_value("(1, 3, 5)")
    other_txt_rows.expect_value("()")
    main_row_count.expect_value("grid: 3; selected: 3")
    other_row_count.expect_value("grid: 0; selected: 0")

    main_clear_btn.click()

    main_txt_rows.expect_value("()")
    other_txt_rows.expect_value("()")
    main_row_count.expect_value("grid: 0; selected: 0")
    other_row_count.expect_value("grid: 0; selected: 0")


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    expect_row_selection(page, "", "card2-")
    expect_row_selection(page, "card2-", "")
