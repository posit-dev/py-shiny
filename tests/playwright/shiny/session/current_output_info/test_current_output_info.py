from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_current_output_info(page: Page, local_app: ShinyAppProc) -> None:

    page.goto(local_app.url)

    # Check that we can get background color from clientdata
    info = controller.OutputText(page, "info")
    info.expect_value("BG color: rgb(255, 255, 255)")

    # Click the dark mode button to change the background color
    dark_mode = controller.InputDarkMode(page, "dark_mode")
    dark_mode.expect_mode("light")
    dark_mode.click()
    dark_mode.expect_mode("dark")

    # Check that the background color has changed
    info.expect_value("BG color: rgb(29, 31, 33)")
