from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_dark_mode_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test basic checkbox group
    basic_dark_mode = controller.InputDarkMode(page, "basic")
    basic_text = controller.OutputText(page, "basic_text")

    basic_text.expect_value("Dark mode value: dark")

    # Test module dark mode
    module_group = controller.InputDarkMode(page, "first-module_dark_mode")
    module_text = controller.OutputText(page, "first-dark_mode_text")

    module_text.expect_value("Dark mode value: dark")

    module_group.click()
    basic_text.expect_value("Dark mode value: light")

    # Bookmark the state
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    basic_dark_mode.click()
    module_text.expect_value("Dark mode value: dark")

    # Reload the page to test bookmark
    page.reload()

    basic_text.expect_value("Dark mode value: light")
    module_text.expect_value("Dark mode value: light")
