from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_bookmark_date_inputs(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test basic date input
    date1 = controller.InputDate(page, "date1")
    date1.expect_label("Default date input:")
    date1.expect_value("2024-01-01")

    text1 = controller.Text(page, "selected_date1")
    text1.expect_text("Selected date: 2024-01-01")

    bookmark_button = controller.InputActionButton(page, "bookmark_button")
