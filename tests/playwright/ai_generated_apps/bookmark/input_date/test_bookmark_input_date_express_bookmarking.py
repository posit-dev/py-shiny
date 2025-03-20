from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_bookmark_date_inputs(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test basic date input
    date1 = controller.InputDate(page, "basic")
    date1.expect_label("Basic date input")
    date1.expect_value("2024-01-01")

    text1 = controller.OutputText(page, "basic_text")
    text1.expect_value("Date value: 2024-01-01")

    module_date = controller.InputDate(page, "first-module_date")
    module_date.expect_label("Module date input")
    module_date.expect_value("2024-01-01")
    module_date.set("2024-02-02")

    text2 = controller.OutputText(page, "first-date_text")
    text2.expect_value("Date value: 2024-02-02")
    text1.expect_value("Date value: 2024-01-01")

    # Bookmark the state
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    date1.set("2024-03-03")
    text1.expect_value("Date value: 2024-03-03")

    module_date.set("2024-04-04")
    text2.expect_value("Date value: 2024-04-04")

    # Reload the page to test bookmark
    page.reload()

    date1.expect_value("2024-01-01")
    text1.expect_value("Date value: 2024-01-01")
    module_date.expect_value("2024-02-02")
    text2.expect_value("Date value: 2024-02-02")
