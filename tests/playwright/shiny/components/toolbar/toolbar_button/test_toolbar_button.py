import re

from conftest import create_app_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.playwright.expect import expect_to_have_class
from shiny.run import ShinyAppProc

app = create_app_fixture("./app.py")


def test_toolbar_button_icon_only(page: Page, app: ShinyAppProc) -> None:
    """Test icon-only button with default tooltip."""
    page.goto(app.url)

    # Find the button using controller
    button = controller.ToolbarInputButton(page, "btn_icon_only")
    expect(button.loc).to_be_visible()
    expect(button.loc).to_be_enabled()

    # Check it has the correct classes (use regex to handle multiple classes)
    expect(button.loc).to_have_class(
        re.compile(r"bslib-toolbar-input-button.*action-button")
    )

    # Icon should be visible, label should be hidden
    expect(button.loc_icon).to_be_visible()
    expect(button.loc_label).to_have_attribute("hidden", "")

    # Should have a tooltip (default behavior for icon-only)
    tooltip = page.locator("#btn_icon_only_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.loc.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Save Document")
    expect(tooltip_content.first).to_be_visible()

    # Click and verify reactive value
    output = page.locator("#output_icon_only")
    expect(output).to_have_text("Icon-only button clicked 0 times")
    button.click()
    expect(output).to_have_text("Icon-only button clicked 1 times")


def test_toolbar_button_with_label(page: Page, app: ShinyAppProc) -> None:
    """Test button with both icon and label shown."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_with_label")
    expect(button.loc).to_be_visible()

    # Both icon and label should be visible
    expect(button.loc_icon).to_be_visible()
    expect(button.loc_label).to_be_visible()
    expect(button.loc_label).to_have_text("Edit")

    # Check button type data attribute
    expect(button.loc).to_have_attribute("data-type", "both")

    # Should NOT have a tooltip (default when show_label=True is tooltip=False)
    tooltip = page.locator("#btn_with_label_tooltip")
    expect(tooltip).not_to_be_attached()

    # Click and verify
    output = page.locator("#output_with_label")
    button.click()
    expect(output).to_have_text("Button with label clicked 1 times")


def test_toolbar_button_custom_tooltip(page: Page, app: ShinyAppProc) -> None:
    """Test button with custom tooltip text."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_custom_tooltip")
    expect(button.loc).to_be_visible()

    # Should have tooltip with custom text
    tooltip = page.locator("#btn_custom_tooltip_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches custom tooltip (not label)
    button.loc.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Remove this item permanently")
    expect(tooltip_content.first).to_be_visible()
    # Verify it does NOT contain the label text
    expect(tooltip_content.first).not_to_contain_text("Delete")


def test_toolbar_button_no_tooltip(page: Page, app: ShinyAppProc) -> None:
    """Test button with tooltip disabled."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_no_tooltip")
    expect(button.loc).to_be_visible()

    # Should NOT have a tooltip
    tooltip = page.locator("#btn_no_tooltip_tooltip")
    expect(tooltip).not_to_be_attached()


def test_toolbar_button_disabled(page: Page, app: ShinyAppProc) -> None:
    """Test disabled button state."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_disabled")
    expect(button.loc).to_be_visible()
    expect(button.loc).to_be_disabled()

    # Should have disabled attribute
    expect(button.loc).to_have_attribute("disabled", "")

    # Should have tooltip element (icon-only, so default tooltip with label text)
    # Note: We can't hover on disabled buttons to show the tooltip, so we just verify it exists
    tooltip = page.locator("#btn_disabled_tooltip")
    expect(tooltip).to_be_attached()

    # Output should stay at 0 clicks
    output = page.locator("#output_disabled")
    expect(output).to_have_text("Disabled button clicked 0 times (should stay 0)")

    # Attempt to click (should not work)
    button.loc.click(force=True)
    expect(output).to_have_text("Disabled button clicked 0 times (should stay 0)")


def test_toolbar_button_border(page: Page, app: ShinyAppProc) -> None:
    """Test button with border."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_border")
    expect(button.loc).to_be_visible()

    # Should have border-1 class (check if class list contains border-1)
    expect_to_have_class(button.loc, "border-1")

    # Should have tooltip (icon-only, so default tooltip with label text)
    tooltip = page.locator("#btn_border_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.loc.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Upload")
    expect(tooltip_content.first).to_be_visible()

    # Click and verify
    output = page.locator("#output_border")
    button.click()
    expect(output).to_have_text("Border button clicked 1 times")


def test_toolbar_button_label_only(page: Page, app: ShinyAppProc) -> None:
    """Test label-only button without icon."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_label_only")
    expect(button.loc).to_be_visible()

    # Label should be visible
    expect(button.loc_label).to_be_visible()
    expect(button.loc_label).to_have_text("Click Me")

    # Should not have an icon
    expect(button.loc_icon).not_to_be_attached()

    # Check button type
    expect(button.loc).to_have_attribute("data-type", "label")

    # Should NOT have a tooltip (default when show_label=True is tooltip=False)
    tooltip = page.locator("#btn_label_only_tooltip")
    expect(tooltip).not_to_be_attached()


def test_update_toolbar_button_label(page: Page, app: ShinyAppProc) -> None:
    """Test updating button label."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_update_label")

    # Initial label
    expect(button.loc_label).to_have_text("Initial")

    # Click to trigger update
    button.click()

    # Label should be updated
    expect(button.loc_label).to_have_text("Updated 1")

    # Click again
    button.click()
    expect(button.loc_label).to_have_text("Updated 2")


def test_update_toolbar_button_icon(page: Page, app: ShinyAppProc) -> None:
    """Test updating button icon."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_update_icon")

    # Should have tooltip (icon-only, so default tooltip with label text)
    tooltip = page.locator("#btn_update_icon_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.loc.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Toggle")
    expect(tooltip_content.first).to_be_visible()

    # Initial icon is "play" with viewBox "0 0 384 512"
    expect(button.loc_icon.locator("svg")).to_have_attribute("viewBox", "0 0 384 512")

    # Click to toggle icon
    button.click()

    # Icon changed to "pause" with viewBox "0 0 320 512"
    expect(button.loc_icon.locator("svg")).to_have_attribute("viewBox", "0 0 320 512")

    # Click again to toggle back to "play"
    button.click()
    expect(button.loc_icon.locator("svg")).to_have_attribute("viewBox", "0 0 384 512")


def test_update_toolbar_button_show_label(page: Page, app: ShinyAppProc) -> None:
    """Test toggling label visibility."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_toggle_label")

    # Initially hidden
    expect(button.loc_label).to_have_attribute("hidden", "")

    # Should have tooltip initially (icon-only, so default tooltip with label text)
    tooltip = page.locator("#btn_toggle_label_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.loc.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Download")
    expect(tooltip_content.first).to_be_visible()

    # Click to show label
    button.click()

    # Label should be visible (hidden attribute should be removed)
    expect(button.loc_label).to_be_visible()

    # Click to hide again
    button.click()
    expect(button.loc_label).to_have_attribute("hidden", "")


def test_update_toolbar_button_disabled(page: Page, app: ShinyAppProc) -> None:
    """Test toggling disabled state."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_toggle_disabled")
    output = page.locator("#output_toggle_disabled")

    # Initially enabled
    expect(button.loc).to_be_enabled()

    # Should have tooltip (icon-only, so default tooltip with label text)
    tooltip = page.locator("#btn_toggle_disabled_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.loc.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Submit")
    expect(tooltip_content.first).to_be_visible()

    # Click once
    button.click()
    expect(output).to_have_text("Toggle disabled button clicked 1 times")

    # Should now be disabled
    expect(button.loc).to_be_disabled()
    expect(button.loc).to_have_attribute("disabled", "")


def test_update_toolbar_button_all_properties(page: Page, app: ShinyAppProc) -> None:
    """Test updating multiple properties at once."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_update_all")

    # Initial state
    expect(button.loc_label).to_have_text("Start")
    expect(button.loc_label).to_have_attribute("hidden", "")
    # Initial icon is "play" with viewBox "0 0 384 512"
    expect(button.loc_icon.locator("svg")).to_have_attribute("viewBox", "0 0 384 512")
    expect(button.loc).to_be_enabled()

    # Should have tooltip initially (icon-only, so default tooltip with label text)
    tooltip = page.locator("#btn_update_all_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.loc.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Start")
    expect(tooltip_content.first).to_be_visible()

    # First click: pause, show label
    button.click()
    expect(button.loc_label).to_have_text("Pause")
    # Check label is visible (hidden attribute removed)
    expect(button.loc_label).to_be_visible()
    # Icon changed to "pause" with viewBox "0 0 320 512"
    expect(button.loc_icon.locator("svg")).to_have_attribute("viewBox", "0 0 320 512")

    # Second click: stop
    button.click()
    expect(button.loc_label).to_have_text("Stop")
    # Icon changed to "stop" with viewBox "0 0 384 512"
    expect(button.loc_icon.locator("svg")).to_have_attribute("viewBox", "0 0 384 512")

    # Third click: reset and disable
    button.click()
    expect(button.loc_label).to_have_text("Start")
    # Icon changed back to "play" with viewBox "0 0 384 512"
    expect(button.loc_icon.locator("svg")).to_have_attribute("viewBox", "0 0 384 512")
    expect(button.loc).to_be_disabled()


def test_update_toolbar_button_reenable(page: Page, app: ShinyAppProc) -> None:
    """Test that a button can be disabled and then re-enabled."""
    page.goto(app.url)

    target_button = controller.ToolbarInputButton(page, "btn_target")
    disable_button = controller.ToolbarInputButton(page, "btn_disable")
    enable_button = controller.ToolbarInputButton(page, "btn_enable")
    output = page.locator("#output_reenable")

    # Initially enabled
    expect(target_button.loc).to_be_enabled()
    expect(output).to_have_text("Target button clicked 0 times")

    # Click target button to verify it works
    target_button.click()
    expect(output).to_have_text("Target button clicked 1 times")

    # Click disable button
    disable_button.click()

    # Target button should now be disabled
    expect(target_button.loc).to_be_disabled()
    expect(target_button.loc).to_have_attribute("disabled", "")

    # Click enable button
    enable_button.click()

    # Target button should now be re-enabled
    expect(target_button.loc).to_be_enabled()
    expect(target_button.loc).not_to_have_attribute("disabled", "")

    # Click target button again to verify it works after re-enabling
    target_button.click()
    expect(output).to_have_text("Target button clicked 2 times")


def test_toolbar_button_aria_attributes(page: Page, app: ShinyAppProc) -> None:
    """Test accessibility attributes."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_icon_only")

    # Should have aria-labelledby pointing to label
    expect(button.loc).to_have_attribute(
        "aria-labelledby", re.compile(r"btn-label-\d+")
    )

    # Icon should be aria-hidden
    expect(button.loc_icon).to_have_attribute("aria-hidden", "true")


def test_toolbar_button_click_count(page: Page, app: ShinyAppProc) -> None:
    """Test that click count increments correctly."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_icon_only")
    output = page.locator("#output_icon_only")

    # Click multiple times
    for i in range(1, 6):
        button.click()
        expect(output).to_have_text(f"Icon-only button clicked {i} times")


def test_toolbar_button_type_attribute(page: Page, app: ShinyAppProc) -> None:
    """Test button type attribute."""
    page.goto(app.url)

    # Icon-only button
    btn_icon = controller.ToolbarInputButton(page, "btn_icon_only")
    expect(btn_icon.loc).to_have_attribute("data-type", "icon")

    # Button with both icon and label
    btn_both = controller.ToolbarInputButton(page, "btn_with_label")
    expect(btn_both.loc).to_have_attribute("data-type", "both")

    # Label-only button
    btn_label = controller.ToolbarInputButton(page, "btn_label_only")
    expect(btn_label.loc).to_have_attribute("data-type", "label")


def test_toolbar_button_custom_data_attributes(page: Page, app: ShinyAppProc) -> None:
    """Test button with custom data attributes passed via kwargs."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_custom_attr")
    expect(button.loc).to_be_visible()

    # Should have custom data attributes
    expect(button.loc).to_have_attribute("data-testid", "custom-button")
    expect(button.loc).to_have_attribute("data-category", "featured")

    # Should also have the standard toolbar button classes
    expect_to_have_class(button.loc, "bslib-toolbar-input-button")
    expect_to_have_class(button.loc, "action-button")

    # Verify button is functional
    output = page.locator("#output_custom_attr")
    expect(output).to_have_text("Custom attr button clicked 0 times")
    button.click()
    expect(output).to_have_text("Custom attr button clicked 1 times")


def test_toolbar_button_custom_class(page: Page, app: ShinyAppProc) -> None:
    """Test button with custom Bootstrap class."""
    page.goto(app.url)

    button = controller.ToolbarInputButton(page, "btn_custom_style")
    expect(button.loc).to_be_visible()

    # Should have btn-danger class
    expect_to_have_class(button.loc, "btn-danger")
    # Should still have standard toolbar classes
    expect_to_have_class(button.loc, "bslib-toolbar-input-button")
    expect_to_have_class(button.loc, "action-button")

    # Label should be visible (show_label=True)
    expect(button.loc_label).to_be_visible()
    expect(button.loc_label).to_have_text("Danger")

    # Verify button is functional
    output = page.locator("#output_custom_style")
    button.click()
    expect(output).to_have_text("Custom style button clicked 1 times")
