from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_checkbox_group_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test basic checkbox group
    basic_group = controller.InputCheckboxGroup(page, "basic")
    basic_group.expect_label("Basic checkbox group")
    basic_group.expect_selected([])

    basic_text = controller.OutputText(page, "basic_text")
    basic_text.expect_value("Checkbox group values: ()")

    # Test module checkbox group
    module_group = controller.InputCheckboxGroup(page, "first-module_checkbox")
    module_group.expect_label("Module checkbox group")
    module_group.expect_selected([])

    module_text = controller.OutputText(page, "first-checkbox_text")
    module_text.expect_value("Checkbox group values: ()")

    # Select values
    basic_group.set(["Option 1", "Option 3"])
    basic_group.expect_selected(["Option 1", "Option 3"])
    basic_text.expect_value("Checkbox group values: ('Option 1', 'Option 3')")

    module_group.set(["Choice A", "Choice C"])
    module_group.expect_selected(["Choice A", "Choice C"])
    module_text.expect_value("Checkbox group values: ('Choice A', 'Choice C')")

    # Bookmark the state
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    # Reload the page to test bookmark
    page.reload()

    # Check if selections are preserved
    basic_group.expect_selected(["Option 1", "Option 3"])
    basic_text.expect_value("Checkbox group values: ('Option 1', 'Option 3')")

    module_group.expect_selected(["Choice A", "Choice C"])
    module_text.expect_value("Checkbox group values: ('Choice A', 'Choice C')")
