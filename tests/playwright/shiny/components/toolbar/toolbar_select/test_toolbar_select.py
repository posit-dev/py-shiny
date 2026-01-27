import re

from conftest import create_app_fixture
from playwright.sync_api import Page, expect

from shiny.run import ShinyAppProc

app = create_app_fixture("./app.py")


def test_toolbar_select_basic(page: Page, app: ShinyAppProc) -> None:
    """Test basic select with list choices."""
    page.goto(app.url)

    # Find the wrapper
    wrapper = page.locator("#select_basic")
    expect(wrapper).to_be_visible()
    expect(wrapper).to_have_class(re.compile(r"bslib-toolbar-input-select"))

    # Find the actual select element
    select = wrapper.locator("select")
    expect(select).to_be_visible()
    expect(select).to_have_class(re.compile(r"bslib-toolbar-select"))

    # Check initial value (first option)
    expect(select).to_have_value("Option 1")
    output = page.locator("#output_basic")
    expect(output).to_have_text("Basic select value: Option 1")

    # Change selection
    select.select_option("Option 2")
    expect(output).to_have_text("Basic select value: Option 2")

    # Label should be hidden by default
    label_span = wrapper.locator(".bslib-toolbar-label")
    expect(label_span).to_have_class(re.compile(r"visually-hidden"))


def test_toolbar_select_dict_choices(page: Page, app: ShinyAppProc) -> None:
    """Test select with dict choices and selected value."""
    page.goto(app.url)

    select = page.locator("#select_dict").locator("select")
    expect(select).to_be_visible()

    # Check that selected value is "active"
    expect(select).to_have_value("active")
    output = page.locator("#output_dict")
    expect(output).to_have_text("Dict select value: active")

    # Verify options exist
    select.select_option("all")
    expect(output).to_have_text("Dict select value: all")

    select.select_option("archived")
    expect(output).to_have_text("Dict select value: archived")


def test_toolbar_select_with_icon(page: Page, app: ShinyAppProc) -> None:
    """Test select with icon."""
    page.goto(app.url)

    wrapper = page.locator("#select_icon")
    expect(wrapper).to_be_visible()

    # Icon should be in the label
    label = wrapper.locator("label")
    icon = label.locator(".bslib-toolbar-icon")
    expect(icon).to_be_visible()
    expect(icon).to_have_attribute("aria-hidden", "true")

    # Select should work normally
    select = wrapper.locator("select")
    expect(select).to_have_value("All")
    select.select_option("Recent")
    output = page.locator("#output_icon")
    expect(output).to_have_text("Icon select value: Recent")


def test_toolbar_select_label_shown(page: Page, app: ShinyAppProc) -> None:
    """Test select with label shown."""
    page.goto(app.url)

    wrapper = page.locator("#select_label_shown")
    label_span = wrapper.locator(".bslib-toolbar-label")

    # Label should be visible (not have visually-hidden class)
    class_attr = label_span.get_attribute("class")
    assert class_attr is not None
    assert "visually-hidden" not in class_attr
    expect(label_span).to_be_visible()
    expect(label_span).to_have_text("Sort by")


def test_toolbar_select_custom_tooltip(page: Page, app: ShinyAppProc) -> None:
    """Test select with custom tooltip."""
    page.goto(app.url)

    wrapper = page.locator("#select_custom_tooltip")
    select = wrapper.locator("select")

    # Should have tooltip with custom text
    select.hover()
    page.wait_for_timeout(100)
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Change how items are displayed")


def test_toolbar_select_no_tooltip(page: Page, app: ShinyAppProc) -> None:
    """Test select with tooltip disabled."""
    page.goto(app.url)

    wrapper = page.locator("#select_no_tooltip")
    select = wrapper.locator("select")

    # Hover should not show tooltip
    select.hover()
    page.wait_for_timeout(100)
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content).not_to_be_visible()


def test_toolbar_select_grouped_choices(page: Page, app: ShinyAppProc) -> None:
    """Test select with grouped choices."""
    page.goto(app.url)

    select = page.locator("#select_grouped").locator("select")
    expect(select).to_be_visible()

    # Check initial value (first option in first group)
    expect(select).to_have_value("a1")
    output = page.locator("#output_grouped")
    expect(output).to_have_text("Grouped select value: a1")

    # Should have optgroups
    optgroups = select.locator("optgroup")
    expect(optgroups).to_have_count(2)

    # Select from second group
    select.select_option("b2")
    expect(output).to_have_text("Grouped select value: b2")


def test_toolbar_select_update_choices(page: Page, app: ShinyAppProc) -> None:
    """Test updating select choices."""
    page.goto(app.url)

    select = page.locator("#select_update_choices").locator("select")
    button = page.locator("#btn_update_choices")
    output = page.locator("#output_update_choices")

    # Initial choices: A, B, C
    expect(select).to_have_value("A")
    expect(output).to_have_text("Update choices value: A")

    # Click to update to X, Y, Z with Y selected
    button.click()
    page.wait_for_timeout(100)
    expect(select).to_have_value("Y")
    expect(output).to_have_text("Update choices value: Y")

    # Click again to switch back to A, B, C with B selected
    button.click()
    page.wait_for_timeout(100)
    expect(select).to_have_value("B")
    expect(output).to_have_text("Update choices value: B")


def test_toolbar_select_update_selected(page: Page, app: ShinyAppProc) -> None:
    """Test updating selected value."""
    page.goto(app.url)

    select = page.locator("#select_update_selected").locator("select")
    button = page.locator("#btn_update_selected")
    output = page.locator("#output_update_selected")

    # Initial: First
    expect(select).to_have_value("First")

    # Click to go to Second
    button.click()
    page.wait_for_timeout(100)
    expect(select).to_have_value("Second")
    expect(output).to_have_text("Update selected value: Second")

    # Click to go to Third
    button.click()
    page.wait_for_timeout(100)
    expect(select).to_have_value("Third")
    expect(output).to_have_text("Update selected value: Third")

    # Click to go back to First
    button.click()
    page.wait_for_timeout(100)
    expect(select).to_have_value("First")
    expect(output).to_have_text("Update selected value: First")


def test_toolbar_select_update_label(page: Page, app: ShinyAppProc) -> None:
    """Test updating select label."""
    page.goto(app.url)

    wrapper = page.locator("#select_update_label")
    button = page.locator("#btn_update_label")
    label_span = wrapper.locator(".bslib-toolbar-label")

    # Initial label
    expect(label_span).to_have_text("Initial Label")

    # Click to update
    button.click()
    page.wait_for_timeout(100)
    expect(label_span).to_have_text("Updated 1")

    # Click again
    button.click()
    page.wait_for_timeout(100)
    expect(label_span).to_have_text("Updated 2")


def test_toolbar_select_toggle_show_label(page: Page, app: ShinyAppProc) -> None:
    """Test toggling label visibility."""
    page.goto(app.url)

    wrapper = page.locator("#select_toggle_show_label")
    button = page.locator("#btn_toggle_show_label")
    label_span = wrapper.locator(".bslib-toolbar-label")

    # Initially hidden
    expect(label_span).to_have_class(re.compile(r"visually-hidden"))

    # Click to show
    button.click()
    page.wait_for_timeout(100)
    class_attr = label_span.get_attribute("class")
    assert class_attr is not None
    assert "visually-hidden" not in class_attr

    # Click to hide again
    button.click()
    page.wait_for_timeout(100)
    expect(label_span).to_have_class(re.compile(r"visually-hidden"))


def test_toolbar_select_update_icon(page: Page, app: ShinyAppProc) -> None:
    """Test updating select icon."""
    page.goto(app.url)

    wrapper = page.locator("#select_update_icon")
    button = page.locator("#btn_update_icon")
    label = wrapper.locator("label")
    icon_container = label.locator(".bslib-toolbar-icon")

    # Get initial icon HTML
    initial_html = icon_container.inner_html()
    assert len(initial_html) > 0

    # Click to update icon
    button.click()
    page.wait_for_timeout(200)
    updated_html = icon_container.inner_html()
    assert updated_html != initial_html
    assert len(updated_html) > 0

    # Click again to toggle back
    button.click()
    page.wait_for_timeout(200)
    final_html = icon_container.inner_html()
    assert final_html != updated_html
    assert len(final_html) > 0


def test_toolbar_select_update_all(page: Page, app: ShinyAppProc) -> None:
    """Test updating all properties at once."""
    page.goto(app.url)

    wrapper = page.locator("#select_update_all")
    select = wrapper.locator("select")
    label_span = wrapper.locator(".bslib-toolbar-label")
    output = page.locator("#output_update_all")

    # Initial state
    expect(select).to_have_value("Active")
    expect(label_span).to_have_text("Status")
    expect(label_span).to_have_class(re.compile(r"visually-hidden"))

    # Change selection to trigger update
    select.select_option("Active")
    page.wait_for_timeout(200)

    # After update: new label, new choices, new selected, icon added, label shown
    expect(label_span).to_have_text("New Status")
    class_attr = label_span.get_attribute("class")
    assert class_attr is not None
    assert "visually-hidden" not in class_attr
    expect(select).to_have_value("Online")
    expect(output).to_have_text("Update all value: Online")

    # Icon should now be present
    label = wrapper.locator("label")
    icon = label.locator(".bslib-toolbar-icon")
    expect(icon).to_be_visible()


def test_toolbar_select_icon_and_label(page: Page, app: ShinyAppProc) -> None:
    """Test select with both icon and label shown."""
    page.goto(app.url)

    wrapper = page.locator("#select_icon_label")
    label = wrapper.locator("label")

    # Icon should be visible
    icon = label.locator(".bslib-toolbar-icon")
    expect(icon).to_be_visible()

    # Label should be visible (not visually-hidden)
    label_span = wrapper.locator(".bslib-toolbar-label")
    expect(label_span).to_be_visible()
    class_attr = label_span.get_attribute("class")
    assert class_attr is not None
    assert "visually-hidden" not in class_attr
    expect(label_span).to_have_text("Priority")


def test_toolbar_select_custom_attributes(page: Page, app: ShinyAppProc) -> None:
    """Test select with custom attributes."""
    page.goto(app.url)

    wrapper = page.locator("#select_custom_attr")
    expect(wrapper).to_be_visible()

    # Should have custom data attributes
    expect(wrapper).to_have_attribute("data-testid", "category-select")
    expect(wrapper).to_have_attribute("data-type", "custom")

    # Select should still work
    select = wrapper.locator("select")
    expect(select).to_have_value("Tech")
    select.select_option("Science")
    output = page.locator("#output_custom_attr")
    expect(output).to_have_text("Custom attr value: Science")


def test_toolbar_select_aria_attributes(page: Page, app: ShinyAppProc) -> None:
    """Test accessibility attributes."""
    page.goto(app.url)

    wrapper = page.locator("#select_basic")
    label = wrapper.locator("label")
    select = wrapper.locator("select")

    # Label should have 'for' attribute pointing to select
    label_for = label.get_attribute("for")
    select_id = select.get_attribute("id")
    assert label_for == select_id

    # Icon should be aria-hidden
    wrapper_icon = page.locator("#select_icon")
    icon = wrapper_icon.locator(".bslib-toolbar-icon")
    expect(icon).to_have_attribute("aria-hidden", "true")


def test_toolbar_select_default_tooltip(page: Page, app: ShinyAppProc) -> None:
    """Test default tooltip behavior (shows label when label is hidden)."""
    page.goto(app.url)

    # Select with hidden label should have tooltip with label text
    wrapper = page.locator("#select_basic")
    select = wrapper.locator("select")

    select.hover()
    page.wait_for_timeout(100)
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Choose option")


def test_toolbar_select_structure(page: Page, app: ShinyAppProc) -> None:
    """Test the overall structure of toolbar_input_select."""
    page.goto(app.url)

    wrapper = page.locator("#select_basic")

    # Should have the correct wrapper classes
    expect(wrapper).to_have_class(
        re.compile(r"bslib-toolbar-input-select.*shiny-input-container")
    )

    # Should contain a label element
    label = wrapper.locator("label")
    expect(label).to_be_attached()

    # Should contain a select element
    select = wrapper.locator("select")
    expect(select).to_be_attached()
    expect(select).to_have_class(re.compile(r"form-select.*bslib-toolbar-select"))
