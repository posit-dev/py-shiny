from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_dark_mode_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test dark mode input
    dark_mode = controller.InputDarkMode(page, "mode")
    dark_mode.expect_mode("light")  # Default mode is light
    dark_mode.click()  # Toggle dark mode
    dark_mode.expect_mode("dark")
    dark_mode.expect_page_mode("dark")  # Check if page mode is updated
