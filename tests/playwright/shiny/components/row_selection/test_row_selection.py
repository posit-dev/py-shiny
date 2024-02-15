from conftest import ShinyAppProc
from controls import InputActionButton, OutputTextVerbatim
from playwright.sync_api import Page


def expect_row_selection(page: Page, prefix_main: str, prefix_secondary: str):
    # TODO: Karan, add Dataframe helpers methods for selected_rows

    output_main = OutputTextVerbatim(page, f"{prefix_main}selected_rows")
    output_secondary = OutputTextVerbatim(page, f"{prefix_secondary}selected_rows")
    select_btn = InputActionButton(page, f"{prefix_main}select")
    clear_btn = InputActionButton(page, f"{prefix_main}clear")
    output_secondary.expect_value("()")
    select_btn.click()
    output_main.expect_value("(1, 3, 5)")
    # Ensure that the other dataframe didn't update
    output_secondary.expect_value("()")
    clear_btn.click()
    output_main.expect_value("()")


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    expect_row_selection(page, "", "card2-")
    expect_row_selection(page, "card2-", "")
