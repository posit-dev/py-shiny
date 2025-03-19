from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_checkbox_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test basic checkbox
    basic_checkbox = controller.InputCheckbox(page, "basic")
    basic_checkbox.expect_label("Basic checkbox")
    basic_checkbox.expect_checked(False)

    basic_text = controller.OutputText(page, "basic_text")
    basic_text.expect_value("Checkbox value: False")

    # Test module checkbox
    module_checkbox = controller.InputCheckbox(page, "first-module_checkbox")
    module_checkbox.expect_label("Basic module checkbox")
    module_checkbox.expect_checked(False)

    module_text = controller.OutputText(page, "first-checkbox_text")
    module_text.expect_value("Checkbox value: False")

    basic_checkbox.set(True)
    basic_checkbox.expect_checked(True)
    basic_text.expect_value("Checkbox value: True")
    module_checkbox.set(True)
    module_checkbox.expect_checked(True)
    module_text.expect_value("Checkbox value: True")

    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    # reload the page to test bookmark
    page.reload()

    # Check if the basic checkbox is checked
    basic_checkbox.expect_checked(True)
    basic_text.expect_value("Checkbox value: True")
    # Check if the module checkbox is checked
    module_checkbox.expect_checked(True)
    module_text.expect_value("Checkbox value: True")
