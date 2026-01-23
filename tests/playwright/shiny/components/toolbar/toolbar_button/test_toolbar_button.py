import re

from conftest import create_app_fixture
from playwright.sync_api import Page, expect

from shiny.run import ShinyAppProc

app = create_app_fixture("./app.py")


def test_toolbar_button_icon_only(page: Page, app: ShinyAppProc) -> None:
    """Test icon-only button with default tooltip."""
    page.goto(app.url)

    # Find the button
    button = page.locator("#btn_icon_only")
    expect(button).to_be_visible()
    expect(button).to_be_enabled()

    # Check it has the correct classes (use regex to handle multiple classes)
    expect(button).to_have_class(
        re.compile(r"bslib-toolbar-input-button.*action-button")
    )

    # Icon should be visible, label should be hidden
    icon = button.locator(".bslib-toolbar-icon")
    expect(icon).to_be_visible()

    label = button.locator(".bslib-toolbar-label")
    expect(label).to_have_attribute("hidden", "")

    # Should have a tooltip (default behavior for icon-only)
    tooltip = page.locator("#btn_icon_only_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.hover()
    page.wait_for_timeout(100)  # Wait for tooltip to appear
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Save Document")

    # Click and verify reactive value
    output = page.locator("#output_icon_only")
    expect(output).to_have_text("Icon-only button clicked 0 times")
    button.click()
    expect(output).to_have_text("Icon-only button clicked 1 times")


def test_toolbar_button_with_label(page: Page, app: ShinyAppProc) -> None:
    """Test button with both icon and label shown."""
    page.goto(app.url)

    button = page.locator("#btn_with_label")
    expect(button).to_be_visible()

    # Both icon and label should be visible
    icon = button.locator(".bslib-toolbar-icon")
    expect(icon).to_be_visible()

    label = button.locator(".bslib-toolbar-label")
    expect(label).to_be_visible()

    # Check that hidden attribute is not present
    hidden_attr = label.get_attribute("hidden")
    assert hidden_attr is None
    expect(label).to_have_text("Edit")

    # Check button type data attribute
    expect(button).to_have_attribute("data-type", "both")

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

    button = page.locator("#btn_custom_tooltip")
    expect(button).to_be_visible()

    # Should have tooltip with custom text
    tooltip = page.locator("#btn_custom_tooltip_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches custom tooltip (not label)
    button.hover()
    page.wait_for_timeout(100)  # Wait for tooltip to appear
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Remove this item permanently")
    # Verify it does NOT contain the label text
    expect(tooltip_content.first).not_to_contain_text("Delete")


def test_toolbar_button_no_tooltip(page: Page, app: ShinyAppProc) -> None:
    """Test button with tooltip disabled."""
    page.goto(app.url)

    button = page.locator("#btn_no_tooltip")
    expect(button).to_be_visible()

    # Should NOT have a tooltip
    tooltip = page.locator("#btn_no_tooltip_tooltip")
    expect(tooltip).not_to_be_attached()


def test_toolbar_button_disabled(page: Page, app: ShinyAppProc) -> None:
    """Test disabled button state."""
    page.goto(app.url)

    button = page.locator("#btn_disabled")
    expect(button).to_be_visible()
    expect(button).to_be_disabled()

    # Should have disabled attribute
    expect(button).to_have_attribute("disabled", "")

    # Should have tooltip element (icon-only, so default tooltip with label text)
    # Note: We can't hover on disabled buttons to show the tooltip, so we just verify it exists
    tooltip = page.locator("#btn_disabled_tooltip")
    expect(tooltip).to_be_attached()

    # Output should stay at 0 clicks
    output = page.locator("#output_disabled")
    expect(output).to_have_text("Disabled button clicked 0 times (should stay 0)")

    # Attempt to click (should not work)
    button.click(force=True)
    page.wait_for_timeout(100)
    expect(output).to_have_text("Disabled button clicked 0 times (should stay 0)")


def test_toolbar_button_border(page: Page, app: ShinyAppProc) -> None:
    """Test button with border."""
    page.goto(app.url)

    button = page.locator("#btn_border")
    expect(button).to_be_visible()

    # Should have border-1 class (check if class list contains border-1)
    class_attr = button.get_attribute("class")
    assert class_attr is not None
    assert "border-1" in class_attr

    # Should have tooltip (icon-only, so default tooltip with label text)
    tooltip = page.locator("#btn_border_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.hover()
    page.wait_for_timeout(100)  # Wait for tooltip to appear
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Upload")

    # Click and verify
    output = page.locator("#output_border")
    button.click()
    expect(output).to_have_text("Border button clicked 1 times")


def test_toolbar_button_label_only(page: Page, app: ShinyAppProc) -> None:
    """Test label-only button without icon."""
    page.goto(app.url)

    button = page.locator("#btn_label_only")
    expect(button).to_be_visible()

    # Label should be visible
    label = button.locator(".bslib-toolbar-label")
    expect(label).to_be_visible()
    expect(label).to_have_text("Click Me")

    # Should not have an icon
    icon = button.locator(".bslib-toolbar-icon")
    expect(icon).not_to_be_attached()

    # Check button type
    expect(button).to_have_attribute("data-type", "label")

    # Should NOT have a tooltip (default when show_label=True is tooltip=False)
    tooltip = page.locator("#btn_label_only_tooltip")
    expect(tooltip).not_to_be_attached()


def test_update_toolbar_button_label(page: Page, app: ShinyAppProc) -> None:
    """Test updating button label."""
    page.goto(app.url)

    button = page.locator("#btn_update_label")
    label = button.locator(".bslib-toolbar-label")

    # Initial label
    expect(label).to_have_text("Initial")

    # Click to trigger update
    button.click()
    page.wait_for_timeout(100)

    # Label should be updated
    expect(label).to_have_text("Updated 1")

    # Click again
    button.click()
    page.wait_for_timeout(100)
    expect(label).to_have_text("Updated 2")


def test_update_toolbar_button_icon(page: Page, app: ShinyAppProc) -> None:
    """Test updating button icon."""
    page.goto(app.url)

    button = page.locator("#btn_update_icon")
    icon_container = button.locator(".bslib-toolbar-icon")

    # Should have tooltip (icon-only, so default tooltip with label text)
    tooltip = page.locator("#btn_update_icon_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.hover()
    page.wait_for_timeout(100)  # Wait for tooltip to appear
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Toggle")

    # Get initial icon HTML
    initial_html = icon_container.inner_html()
    initial_len = len(initial_html)
    assert initial_len > 0

    # Click to toggle icon
    button.click()
    page.wait_for_timeout(200)

    # Icon HTML should have changed (content updated)
    updated_html = icon_container.inner_html()
    assert len(updated_html) > 0
    assert updated_html != initial_html
    # Note: We can't reliably check icon names in faicons SVG output

    # Click again to toggle back
    button.click()
    page.wait_for_timeout(200)
    final_html = icon_container.inner_html()
    assert len(final_html) > 0


def test_update_toolbar_button_show_label(page: Page, app: ShinyAppProc) -> None:
    """Test toggling label visibility."""
    page.goto(app.url)

    button = page.locator("#btn_toggle_label")
    label = button.locator(".bslib-toolbar-label")

    # Initially hidden
    expect(label).to_have_attribute("hidden", "")

    # Should have tooltip initially (icon-only, so default tooltip with label text)
    tooltip = page.locator("#btn_toggle_label_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.hover()
    page.wait_for_timeout(100)  # Wait for tooltip to appear
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Download")

    # Click to show label
    button.click()
    page.wait_for_timeout(200)

    # Label should be visible (hidden attribute should be removed)
    hidden_attr = label.get_attribute("hidden")
    assert hidden_attr is None
    expect(label).to_be_visible()

    # Click to hide again
    button.click()
    page.wait_for_timeout(200)
    expect(label).to_have_attribute("hidden", "")


def test_update_toolbar_button_disabled(page: Page, app: ShinyAppProc) -> None:
    """Test toggling disabled state."""
    page.goto(app.url)

    button = page.locator("#btn_toggle_disabled")
    output = page.locator("#output_toggle_disabled")

    # Initially enabled
    expect(button).to_be_enabled()

    # Should have tooltip (icon-only, so default tooltip with label text)
    tooltip = page.locator("#btn_toggle_disabled_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.hover()
    page.wait_for_timeout(100)  # Wait for tooltip to appear
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Submit")

    # Click once
    button.click()
    page.wait_for_timeout(100)
    expect(output).to_have_text("Toggle disabled button clicked 1 times")

    # Should now be disabled
    expect(button).to_be_disabled()
    expect(button).to_have_attribute("disabled", "")


def test_update_toolbar_button_all_properties(page: Page, app: ShinyAppProc) -> None:
    """Test updating multiple properties at once."""
    page.goto(app.url)

    button = page.locator("#btn_update_all")
    label = button.locator(".bslib-toolbar-label")
    icon_container = button.locator(".bslib-toolbar-icon")
    output = page.locator("#output_update_all")

    # Initial state
    expect(label).to_have_text("Start")
    expect(label).to_have_attribute("hidden", "")
    icon_html = icon_container.inner_html()
    assert len(icon_html) > 0  # Just verify icon is present
    expect(button).to_be_enabled()

    # Should have tooltip initially (icon-only, so default tooltip with label text)
    tooltip = page.locator("#btn_update_all_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches label
    button.hover()
    page.wait_for_timeout(100)  # Wait for tooltip to appear
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Start")

    # First click: pause, show label
    button.click()
    page.wait_for_timeout(200)
    expect(label).to_have_text("Pause")
    # Check hidden attribute is removed
    hidden_attr = label.get_attribute("hidden")
    assert hidden_attr is None
    second_icon_html = icon_container.inner_html()
    # Just verify icon container has content (icon names aren't in SVG paths)
    assert second_icon_html != icon_html
    assert len(second_icon_html) > 0

    # Second click: stop
    button.click()
    page.wait_for_timeout(200)
    expect(label).to_have_text("Stop")
    icon_html = icon_container.inner_html()
    assert second_icon_html != icon_html
    assert len(icon_html) > 0

    # Third click: reset and disable
    button.click()
    page.wait_for_timeout(200)
    expect(label).to_have_text("Start")
    third_icon_html = icon_container.inner_html()
    assert third_icon_html != icon_html

    assert len(third_icon_html) > 0
    expect(button).to_be_disabled()


def test_toolbar_button_aria_attributes(page: Page, app: ShinyAppProc) -> None:
    """Test accessibility attributes."""
    page.goto(app.url)

    button = page.locator("#btn_icon_only")

    # Should have aria-labelledby pointing to label
    aria_labelledby = button.get_attribute("aria-labelledby")
    assert aria_labelledby is not None
    assert "btn-label-" in aria_labelledby

    # Icon should be aria-hidden
    icon = button.locator(".bslib-toolbar-icon")
    expect(icon).to_have_attribute("aria-hidden", "true")


def test_toolbar_button_click_count(page: Page, app: ShinyAppProc) -> None:
    """Test that click count increments correctly."""
    page.goto(app.url)

    button = page.locator("#btn_icon_only")
    output = page.locator("#output_icon_only")

    # Click multiple times
    for i in range(1, 6):
        button.click()
        page.wait_for_timeout(50)
        expect(output).to_have_text(f"Icon-only button clicked {i} times")


def test_toolbar_button_type_attribute(page: Page, app: ShinyAppProc) -> None:
    """Test button type attribute."""
    page.goto(app.url)

    # Icon-only button
    btn_icon = page.locator("#btn_icon_only")
    expect(btn_icon).to_have_attribute("data-type", "icon")

    # Button with both icon and label
    btn_both = page.locator("#btn_with_label")
    expect(btn_both).to_have_attribute("data-type", "both")

    # Label-only button
    btn_label = page.locator("#btn_label_only")
    expect(btn_label).to_have_attribute("data-type", "label")


def test_toolbar_button_custom_data_attributes(page: Page, app: ShinyAppProc) -> None:
    """Test button with custom data attributes passed via kwargs."""
    page.goto(app.url)

    button = page.locator("#btn_custom_attr")
    expect(button).to_be_visible()

    # Should have custom data attributes
    expect(button).to_have_attribute("data-testid", "custom-button")
    expect(button).to_have_attribute("data-category", "featured")

    # Should also have the standard toolbar button classes
    class_attr = button.get_attribute("class")
    assert class_attr is not None
    assert "bslib-toolbar-input-button" in class_attr
    assert "action-button" in class_attr

    # Verify button is functional
    output = page.locator("#output_custom_attr")
    expect(output).to_have_text("Custom attr button clicked 0 times")
    button.click()
    expect(output).to_have_text("Custom attr button clicked 1 times")


def test_toolbar_button_custom_class(page: Page, app: ShinyAppProc) -> None:
    """Test button with custom Bootstrap class."""
    page.goto(app.url)

    button = page.locator("#btn_custom_style")
    expect(button).to_be_visible()

    # Should have btn-danger class
    class_attr = button.get_attribute("class")
    assert class_attr is not None
    assert "btn-danger" in class_attr
    # Should still have standard toolbar classes
    assert "bslib-toolbar-input-button" in class_attr
    assert "action-button" in class_attr

    # Label should be visible (show_label=True)
    label = button.locator(".bslib-toolbar-label")
    expect(label).to_be_visible()
    expect(label).to_have_text("Danger")

    # Verify button is functional
    output = page.locator("#output_custom_style")
    button.click()
    expect(output).to_have_text("Custom style button clicked 1 times")
