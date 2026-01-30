"""Test the toolbar controller expect methods."""

import re

from conftest import create_app_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_app_fixture("./toolbar_button/app.py")


def test_toolbar_button_expect_label(page: Page, app: ShinyAppProc) -> None:
    """Test ToolbarInputButton.expect_label()."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_icon_only")
    button.expect_label("Save Document")

    # Test updating label
    button_update = controller.ToolbarInputButton(page, "btn_update_label")
    button_update.expect_label("Initial")
    button_update.click()
    page.wait_for_timeout(100)
    button_update.expect_label("Updated 1")


def test_toolbar_button_expect_icon(page: Page, app: ShinyAppProc) -> None:
    """Test ToolbarInputButton.expect_icon()."""
    page.goto(app.url)

    # Button with icon should have icon
    button_with_icon = controller.ToolbarInputButton(page, "btn_icon_only")
    button_with_icon.expect_icon(exists=True)

    # Button without icon should not have icon
    button_no_icon = controller.ToolbarInputButton(page, "btn_label_only")
    button_no_icon.expect_icon(exists=False)


def test_toolbar_button_expect_icon_visible(page: Page, app: ShinyAppProc) -> None:
    """Test ToolbarInputButton.expect_icon_visible()."""
    page.goto(app.url)

    # Button with icon should have visible icon
    button_with_icon = controller.ToolbarInputButton(page, "btn_icon_only")
    button_with_icon.expect_icon_visible(visible=True)

    # Button with both icon and label should have visible icon
    button_both = controller.ToolbarInputButton(page, "btn_with_label")
    button_both.expect_icon_visible(visible=True)


def test_toolbar_button_no_icon(page: Page, app: ShinyAppProc) -> None:
    """Test that buttons without icons properly report no icon."""
    page.goto(app.url)

    # Label-only button should not have icon element
    button_label_only = controller.ToolbarInputButton(page, "btn_label_only")
    button_label_only.expect_icon(exists=False)

    # Since icon doesn't exist, we can't check visibility - but we can verify
    # the icon locator count is 0
    expect(button_label_only.loc_icon).to_have_count(0)


def test_toolbar_button_expect_label_visible(page: Page, app: ShinyAppProc) -> None:
    """Test ToolbarInputButton.expect_label_visible() for visible labels."""
    page.goto(app.url)

    # Button with label shown: label visible
    button_with_label = controller.ToolbarInputButton(page, "btn_with_label")
    button_with_label.expect_label_visible(visible=True)

    # Label-only button: label visible
    button_label_only = controller.ToolbarInputButton(page, "btn_label_only")
    button_label_only.expect_label_visible(visible=True)


def test_toolbar_button_expect_label_hidden(page: Page, app: ShinyAppProc) -> None:
    """Test ToolbarInputButton.expect_label_visible() for hidden labels."""
    page.goto(app.url)

    # Icon-only button: label hidden
    button_icon_only = controller.ToolbarInputButton(page, "btn_icon_only")
    button_icon_only.expect_label_visible(visible=False)

    # Custom tooltip button: label hidden
    button_custom_tooltip = controller.ToolbarInputButton(page, "btn_custom_tooltip")
    button_custom_tooltip.expect_label_visible(visible=False)

    # No tooltip button: label hidden
    button_no_tooltip = controller.ToolbarInputButton(page, "btn_no_tooltip")
    button_no_tooltip.expect_label_visible(visible=False)


def test_toolbar_button_toggle_label_visibility(page: Page, app: ShinyAppProc) -> None:
    """Test toggling label visibility dynamically."""
    page.goto(app.url)

    # Test toggling visibility
    button_toggle = controller.ToolbarInputButton(page, "btn_toggle_label")
    button_toggle.expect_label_visible(visible=False)
    button_toggle.click()
    page.wait_for_timeout(200)
    button_toggle.expect_label_visible(visible=True)
    button_toggle.click()
    page.wait_for_timeout(200)
    button_toggle.expect_label_visible(visible=False)


def test_toolbar_button_expect_disabled(page: Page, app: ShinyAppProc) -> None:
    """Test ToolbarInputButton.expect_disabled()."""
    page.goto(app.url)

    # Enabled button
    button_enabled = controller.ToolbarInputButton(page, "btn_icon_only")
    button_enabled.expect_disabled(value=False)

    # Disabled button
    button_disabled = controller.ToolbarInputButton(page, "btn_disabled")
    button_disabled.expect_disabled(value=True)

    # Test toggling disabled state
    button_toggle = controller.ToolbarInputButton(page, "btn_toggle_disabled")
    button_toggle.expect_disabled(value=False)
    button_toggle.click()
    page.wait_for_timeout(100)
    button_toggle.expect_disabled(value=True)


def test_toolbar_button_expect_border(page: Page, app: ShinyAppProc) -> None:
    """Test ToolbarInputButton.expect_border()."""
    page.goto(app.url)

    # Button with border
    button_border = controller.ToolbarInputButton(page, "btn_border")
    button_border.expect_border(has_border=True)

    # Button without border (default)
    button_no_border = controller.ToolbarInputButton(page, "btn_icon_only")
    button_no_border.expect_border(has_border=False)


# Test ToolbarInputSelect controller methods
app_select = create_app_fixture("./toolbar_select/app.py")


def test_toolbar_select_expect_label(page: Page, app_select: ShinyAppProc) -> None:
    """Test ToolbarInputSelect.expect_label()."""
    page.goto(app_select.url)

    select = controller.ToolbarInputSelect(page, "select_basic")
    select.expect_label("Choose option")

    # Test updating label
    select_update = controller.ToolbarInputSelect(page, "select_update_label")
    select_update.expect_label("Initial Label")
    button = page.locator("#btn_update_label")
    button.click()
    page.wait_for_timeout(100)
    select_update.expect_label("Updated 1")


def test_toolbar_select_expect_icon(page: Page, app_select: ShinyAppProc) -> None:
    """Test ToolbarInputSelect.expect_icon()."""
    page.goto(app_select.url)

    # Select with icon
    select_with_icon = controller.ToolbarInputSelect(page, "select_icon")
    select_with_icon.expect_icon(exists=True)

    # Select without icon
    select_no_icon = controller.ToolbarInputSelect(page, "select_basic")
    select_no_icon.expect_icon(exists=True)  # Empty icon container still exists


def test_toolbar_select_expect_icon_visible(
    page: Page, app_select: ShinyAppProc
) -> None:
    """Test ToolbarInputSelect.expect_icon_visible()."""
    page.goto(app_select.url)

    # Select with icon content should have visible icon
    select_with_icon = controller.ToolbarInputSelect(page, "select_icon")
    select_with_icon.expect_icon_visible(visible=True)

    # Select with icon and label shown should have visible icon
    select_icon_label = controller.ToolbarInputSelect(page, "select_icon_label")
    select_icon_label.expect_icon_visible(visible=True)


def test_toolbar_select_empty_icon_not_visible(
    page: Page, app_select: ShinyAppProc
) -> None:
    """Test that selects with empty icon containers report icon as not visible."""
    page.goto(app_select.url)

    # Select without icon content - icon element exists but should not be visible
    select_no_icon = controller.ToolbarInputSelect(page, "select_basic")
    select_no_icon.expect_icon(exists=True)  # Container exists
    select_no_icon.expect_icon_visible(visible=False)  # But it's not visible

    # Same for dict select without icon
    select_dict = controller.ToolbarInputSelect(page, "select_dict")
    select_dict.expect_icon(exists=True)  # Container exists
    select_dict.expect_icon_visible(visible=False)  # But it's not visible


def test_toolbar_select_expect_label_visible(
    page: Page, app_select: ShinyAppProc
) -> None:
    """Test ToolbarInputSelect.expect_label_visible() for visible labels."""
    page.goto(app_select.url)

    # Label shown
    select_shown = controller.ToolbarInputSelect(page, "select_label_shown")
    select_shown.expect_label_visible(visible=True)

    # Select with icon and label both visible
    select_icon_label = controller.ToolbarInputSelect(page, "select_icon_label")
    select_icon_label.expect_label_visible(visible=True)


def test_toolbar_select_expect_label_hidden(
    page: Page, app_select: ShinyAppProc
) -> None:
    """Test ToolbarInputSelect.expect_label_visible() for hidden labels."""
    page.goto(app_select.url)

    # Label hidden by default
    select_hidden = controller.ToolbarInputSelect(page, "select_basic")
    select_hidden.expect_label_visible(visible=False)

    # Dict select with hidden label
    select_dict = controller.ToolbarInputSelect(page, "select_dict")
    select_dict.expect_label_visible(visible=False)

    # Select with icon but hidden label
    select_icon = controller.ToolbarInputSelect(page, "select_icon")
    select_icon.expect_label_visible(visible=False)

    # Grouped select with hidden label
    select_grouped = controller.ToolbarInputSelect(page, "select_grouped")
    select_grouped.expect_label_visible(visible=False)


def test_toolbar_select_toggle_label_visibility(
    page: Page, app_select: ShinyAppProc
) -> None:
    """Test toggling select label visibility dynamically."""
    page.goto(app_select.url)

    # Test toggling visibility
    select_toggle = controller.ToolbarInputSelect(page, "select_toggle_show_label")
    select_toggle.expect_label_visible(visible=False)
    button = page.locator("#btn_toggle_show_label")
    button.click()
    page.wait_for_timeout(100)
    select_toggle.expect_label_visible(visible=True)
    button.click()
    page.wait_for_timeout(100)
    select_toggle.expect_label_visible(visible=False)


def test_toolbar_select_expect_choices(page: Page, app_select: ShinyAppProc) -> None:
    """Test ToolbarInputSelect.expect_choices()."""
    page.goto(app_select.url)

    # List choices
    select_basic = controller.ToolbarInputSelect(page, "select_basic")
    select_basic.expect_choices(["Option 1", "Option 2", "Option 3"])

    # Dict choices (values, not labels)
    select_dict = controller.ToolbarInputSelect(page, "select_dict")
    select_dict.expect_choices(["all", "active", "archived"])

    # Test updating choices
    select_update = controller.ToolbarInputSelect(page, "select_update_choices")
    select_update.expect_choices(["A", "B", "C"])
    button = page.locator("#btn_update_choices")
    button.click()
    page.wait_for_timeout(100)
    select_update.expect_choices(["X", "Y", "Z"])


def test_toolbar_select_expect_selected(page: Page, app_select: ShinyAppProc) -> None:
    """Test ToolbarInputSelect.expect_selected()."""
    page.goto(app_select.url)

    # Default selection (first option)
    select_basic = controller.ToolbarInputSelect(page, "select_basic")
    select_basic.expect_selected("Option 1")

    # Explicit selection
    select_dict = controller.ToolbarInputSelect(page, "select_dict")
    select_dict.expect_selected("active")

    # Test changing selection
    select_basic.set("Option 2")
    select_basic.expect_selected("Option 2")

    # Test updating selected
    select_update = controller.ToolbarInputSelect(page, "select_update_selected")
    select_update.expect_selected("First")
    button = page.locator("#btn_update_selected")
    button.click()
    page.wait_for_timeout(100)
    select_update.expect_selected("Second")


def test_toolbar_select_expect_choice_groups(
    page: Page, app_select: ShinyAppProc
) -> None:
    """Test ToolbarInputSelect.expect_choice_groups()."""
    page.goto(app_select.url)

    # No groups
    select_basic = controller.ToolbarInputSelect(page, "select_basic")
    select_basic.expect_choice_groups([])

    # With groups
    select_grouped = controller.ToolbarInputSelect(page, "select_grouped")
    select_grouped.expect_choice_groups(["Group A", "Group B"])


def test_toolbar_select_set(page: Page, app_select: ShinyAppProc) -> None:
    """Test ToolbarInputSelect.set() method."""
    page.goto(app_select.url)

    select = controller.ToolbarInputSelect(page, "select_basic")
    output = page.locator("#output_basic")

    # Initial value
    expect(output).to_have_text("Basic select value: Option 1")

    # Change value
    select.set("Option 2")
    expect(output).to_have_text("Basic select value: Option 2")

    # Change again
    select.set("Option 3")
    expect(output).to_have_text("Basic select value: Option 3")


def test_toolbar_button_all_methods_together(page: Page, app: ShinyAppProc) -> None:
    """Test multiple controller methods work together correctly."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_icon_only")

    # Test all expect methods at once
    button.expect_label("Save Document")
    button.expect_icon(exists=True)
    button.expect_icon_visible(visible=True)
    button.expect_label_visible(visible=False)
    button.expect_disabled(value=False)
    button.expect_border(has_border=False)

    # Verify button is clickable
    expect(button.loc).to_be_visible()
    expect(button.loc).to_be_enabled()

    # Click and verify reactive behavior
    output = page.locator("#output_icon_only")
    expect(output).to_have_text("Icon-only button clicked 0 times")
    button.click()
    expect(output).to_have_text("Icon-only button clicked 1 times")


def test_toolbar_select_all_methods_together(
    page: Page, app_select: ShinyAppProc
) -> None:
    """Test multiple select controller methods work together correctly."""
    page.goto(app_select.url)

    # Use select with icon for comprehensive testing
    select = controller.ToolbarInputSelect(page, "select_icon")
    output = page.locator("#output_icon")

    # Test all expect methods at once
    select.expect_label("Filter data")
    select.expect_icon(exists=True)
    select.expect_icon_visible(visible=True)
    select.expect_label_visible(visible=False)
    select.expect_choices(["All", "Recent", "Archived"])
    select.expect_selected("All")
    select.expect_choice_groups([])

    # Verify select works
    expect(output).to_have_text("Icon select value: All")
    select.set("Recent")
    expect(output).to_have_text("Icon select value: Recent")
    select.expect_selected("Recent")
