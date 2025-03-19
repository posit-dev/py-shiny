from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_slider_parameters(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test basic numeric slider
    slider1 = controller.InputSlider(page, "basic")
    value1 = controller.OutputText(page, "basic_text")

    slider1.expect_value("50")
    value1.expect_value("Slider value: 50")

    mod_slider1 = controller.InputSlider(page, "first-module_slider")
    mod_value1 = controller.OutputText(page, "first-slider_text")

    mod_slider1.expect_value("50")
    mod_value1.expect_value("Slider value: 50")

    # Change the basic slider value
    slider1.set("75")
    value1.expect_value("Slider value: 75")

    # Change the module slider value
    mod_slider1.set("25")
    mod_value1.expect_value("Slider value: 25")

    # click bookmark button
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    # Change the basic slider value again
    slider1.set("100")
    value1.expect_value("Slider value: 100")

    # Change the module slider value again
    mod_slider1.set("0")
    mod_value1.expect_value("Slider value: 0")

    # Reload the page to test bookmark
    page.reload()

    value1.expect_value("Slider value: 75")
    mod_value1.expect_value("Slider value: 25")
