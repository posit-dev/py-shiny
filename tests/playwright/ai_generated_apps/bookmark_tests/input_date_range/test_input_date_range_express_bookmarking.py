from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_date_range_input(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Initialize the date range input controller
    date_range = controller.InputDateRange(page, "basic")

    # Check initial state
    date_range.expect_label("Basic date range")

    basic_text = controller.OutputText(page, "basic_text")
    basic_text.expect_value(
        "Date range values: (datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))"
    )

    mod_date_range = controller.InputDateRange(page, "first-module_date_range")
    mod_date_range.expect_label("Module date range")
    mod_date_range.set(("2023-06-01", "2023-06-30"))

    mod_date_range_txt = controller.OutputText(page, "first-date_text")
    mod_date_range_txt.expect_value(
        "Date range values: (datetime.date(2023, 6, 1), datetime.date(2023, 6, 30))"
    )

    # Change the date range values
    date_range.set(("2024-01-01", "2024-01-31"))
    basic_text.expect_value(
        "Date range values: (datetime.date(2024, 1, 1), datetime.date(2024, 1, 31))"
    )

    mod_date_range.set(("2024-02-01", "2024-02-28"))
    mod_date_range_txt.expect_value(
        "Date range values: (datetime.date(2024, 2, 1), datetime.date(2024, 2, 28))"
    )

    # click bookmark button
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    mod_date_range.set(("2024-03-01", "2024-03-31"))
    mod_date_range_txt.expect_value(
        "Date range values: (datetime.date(2024, 3, 1), datetime.date(2024, 3, 31))"
    )

    # Reload the page to test bookmark
    page.reload()

    basic_text.expect_value(
        "Date range values: (datetime.date(2024, 1, 1), datetime.date(2024, 1, 31))"
    )

    mod_date_range_txt.expect_value(
        "Date range values: (datetime.date(2024, 2, 1), datetime.date(2024, 2, 28))"
    )
