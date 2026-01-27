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

    # Check initial value (first option autoselected)
    expect(select).to_have_value("Option 1")
    output = page.locator("#output_basic")
    expect(output).to_have_text("Basic select value: Option 1")

    # Change selection
    select.select_option("Option 2")
    expect(output).to_have_text("Basic select value: Option 2")

    # Label should be hidden by default
    label_span = wrapper.locator(".bslib-toolbar-label")
    expect(label_span).to_have_class(re.compile(r"visually-hidden"))

    # Should have default tooltip with label text (label hidden)
    tooltip = page.locator("#select_basic_tooltip")
    expect(tooltip).to_be_attached()

    # Verify tooltip shows label text
    select.hover()
    page.wait_for_timeout(100)
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Choose option")


def test_toolbar_select_dict_choices(page: Page, app: ShinyAppProc) -> None:
    """Test select with dict choices and selected value."""
    page.goto(app.url)

    wrapper = page.locator("#select_dict")
    select = wrapper.locator("select")
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

    # Should have default tooltip with label text (label hidden by default)
    tooltip = page.locator("#select_dict_tooltip")
    expect(tooltip).to_be_attached()

    # Verify tooltip shows label text
    select.hover()
    page.wait_for_timeout(100)
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Filter")


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

    # Should have default tooltip with label text (icon-only, label hidden)
    tooltip = page.locator("#select_icon_tooltip")
    expect(tooltip).to_be_attached()

    # Select should work normally
    select = wrapper.locator("select")
    expect(select).to_have_value("All")
    select.select_option("Recent")
    output = page.locator("#output_icon")
    expect(output).to_have_text("Icon select value: Recent")

    # Verify tooltip shows label text
    select.hover()
    page.wait_for_timeout(100)
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Filter data")


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

    # Should NOT have default tooltip when label is shown
    tooltip = page.locator("#select_label_shown_tooltip")
    expect(tooltip).not_to_be_attached()


def test_toolbar_select_custom_tooltip(page: Page, app: ShinyAppProc) -> None:
    """Test select with custom tooltip."""
    page.goto(app.url)

    wrapper = page.locator("#select_custom_tooltip")
    select = wrapper.locator("select")

    # Should have tooltip element
    tooltip = page.locator("#select_custom_tooltip_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches custom tooltip (not label)
    select.hover()
    page.wait_for_timeout(100)
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Change how items are displayed")
    # Verify it does NOT contain the label text
    expect(tooltip_content.first).not_to_contain_text("View mode")


def test_toolbar_select_no_tooltip(page: Page, app: ShinyAppProc) -> None:
    """Test select with tooltip disabled."""
    page.goto(app.url)

    wrapper = page.locator("#select_no_tooltip")
    select = wrapper.locator("select")

    # Should NOT have a tooltip element
    tooltip = page.locator("#select_no_tooltip_tooltip")
    expect(tooltip).not_to_be_attached()

    # Hover should not show tooltip
    select.hover()
    page.wait_for_timeout(100)
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content).not_to_be_visible()


def test_toolbar_select_grouped_choices(page: Page, app: ShinyAppProc) -> None:
    """Test select with grouped choices."""
    page.goto(app.url)

    wrapper = page.locator("#select_grouped")
    select = wrapper.locator("select")
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

    # Should have default tooltip with label text (label hidden by default)
    tooltip = page.locator("#select_grouped_tooltip")
    expect(tooltip).to_be_attached()

    # Verify tooltip shows label text
    select.hover()
    page.wait_for_timeout(100)
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Select item")


def test_toolbar_select_update_choices(page: Page, app: ShinyAppProc) -> None:
    """Test updating select choices."""
    page.goto(app.url)

    select = page.locator("#select_update_choices").locator("select")
    button = page.locator("#btn_update_choices")
    output = page.locator("#output_update_choices")

    # Initial choices: A, B, C
    expect(select).to_have_value("A")
    expect(output).to_have_text("Update choices value: A")

    # Click to update to X, Y, Z
    button.click()
    page.wait_for_timeout(100)
    # "A" should still show as selected in the render.text even though it is no longer
    # in the choices because we have not selected a new value yet and we did not specify
    #  selected in the serverside update, so the input value retains its original
    expect(output).to_have_text("Update choices value: A")
    options = select.locator("option")
    expect(options).to_have_count(3)

    # Verify each option's value and text
    expect(options.nth(0)).to_have_attribute("value", "X")
    expect(options.nth(0)).to_have_text("X")

    expect(options.nth(1)).to_have_attribute("value", "Y")
    expect(options.nth(1)).to_have_text("Y")

    expect(options.nth(2)).to_have_attribute("value", "Z")
    expect(options.nth(2)).to_have_text("Z")

    # Click again to switch back to A, B, C with B selected
    button.click()
    page.wait_for_timeout(100)
    # Now the selected value should change when options are updated because a selected
    # value was provided in the server update
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
    expect(select).to_have_value("Inactive")
    expect(label_span).to_have_text("Status")
    expect(label_span).to_have_class(re.compile(r"visually-hidden"))

    # Change selection to trigger update
    select.select_option("Active")
    page.wait_for_timeout(500)

    # After update: new label, new choices, new selected, icon added, label shown
    expect(label_span).to_have_text("New Status")
    class_attr = label_span.get_attribute("class")
    assert class_attr is not None
    assert "visually-hidden" not in class_attr
    expect(select).to_have_value("Online")
    expect(output).to_have_text("Update all value: Online")

    # Icon should now be visible (was added by update)
    label = wrapper.locator("label")
    icon = label.locator(".bslib-toolbar-icon")
    expect(icon).to_be_visible()
    # Verify icon has content
    icon_html = icon.inner_html()
    assert len(icon_html) > 0


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

    # Should NOT have default tooltip when label is shown (even with icon)
    tooltip = page.locator("#select_icon_label_tooltip")
    expect(tooltip).not_to_be_attached()


def test_toolbar_select_custom_attributes(page: Page, app: ShinyAppProc) -> None:
    """Test select with custom attributes."""
    page.goto(app.url)

    wrapper = page.locator("#select_custom_attr")
    expect(wrapper).to_be_visible()

    # Should have custom data attributes
    expect(wrapper).to_have_attribute("data-testid", "category-select")
    expect(wrapper).to_have_attribute("style", "background-color: #f9b928;")

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
