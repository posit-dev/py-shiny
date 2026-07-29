import re

import pytest
from conftest import create_app_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.playwright.expect import expect_not_to_have_class
from shiny.run import ShinyAppProc

app = create_app_fixture("./app.py")


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_basic(page: Page, app: ShinyAppProc) -> None:
    """Test basic select with list choices."""
    page.goto(app.url)

    # Find the controller
    select_ctrl = controller.ToolbarInputSelect(page, "select_basic")
    expect(select_ctrl.loc).to_be_visible()
    expect(select_ctrl.loc).to_have_class(re.compile(r"bslib-toolbar-input-select"))

    # Find the actual select element
    expect(select_ctrl.loc_select).to_be_visible()
    expect(select_ctrl.loc_select).to_have_class(re.compile(r"bslib-toolbar-select"))

    # Check initial value (first option autoselected)
    select_ctrl.expect_selected("Option 1")
    output = page.locator("#output_basic")
    expect(output).to_have_text("Basic select value: Option 1")

    # Change selection
    select_ctrl.set("Option 2")
    expect(output).to_have_text("Basic select value: Option 2")

    # Label should be hidden by default
    expect(select_ctrl.loc_label).to_have_class(re.compile(r"visually-hidden"))

    # Should have default tooltip with label text (label hidden)
    tooltip = page.locator("#select_basic_tooltip")
    expect(tooltip).to_be_attached()

    # Verify tooltip shows label text
    select_ctrl.loc_select.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Choose option")


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_dict_choices(page: Page, app: ShinyAppProc) -> None:
    """Test select with dict choices and selected value."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_dict")
    expect(select_ctrl.loc_select).to_be_visible()

    # Check that selected value is "active"
    select_ctrl.expect_selected("active")
    output = page.locator("#output_dict")
    expect(output).to_have_text("Dict select value: active")

    # Verify options exist
    select_ctrl.set("all")
    expect(output).to_have_text("Dict select value: all")

    select_ctrl.set("archived")
    expect(output).to_have_text("Dict select value: archived")

    # Should have default tooltip with label text (label hidden by default)
    tooltip = page.locator("#select_dict_tooltip")
    expect(tooltip).to_be_attached()

    # Verify tooltip shows label text
    select_ctrl.loc_select.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Filter")


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_with_icon(page: Page, app: ShinyAppProc) -> None:
    """Test select with icon."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_icon")
    expect(select_ctrl.loc).to_be_visible()

    # Icon should be in the label
    expect(select_ctrl.loc_icon).to_be_visible()
    expect(select_ctrl.loc_icon).to_have_attribute("aria-hidden", "true")

    # Should have default tooltip with label text (icon-only, label hidden)
    tooltip = page.locator("#select_icon_tooltip")
    expect(tooltip).to_be_attached()

    # Select should work normally
    select_ctrl.expect_selected("All")
    select_ctrl.set("Recent")
    output = page.locator("#output_icon")
    expect(output).to_have_text("Icon select value: Recent")

    # Verify tooltip shows label text
    select_ctrl.loc_select.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_contain_text("Filter data")


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_label_shown(page: Page, app: ShinyAppProc) -> None:
    """Test select with label shown."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_label_shown")

    # Label should be visible (not have visually-hidden class)
    expect_not_to_have_class(select_ctrl.loc_label, "visually-hidden")
    expect(select_ctrl.loc_label).to_be_visible()
    expect(select_ctrl.loc_label).to_have_text("Sort by")

    # Should NOT have default tooltip when label is shown
    tooltip = page.locator("#select_label_shown_tooltip")
    expect(tooltip).not_to_be_attached()


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_custom_tooltip(page: Page, app: ShinyAppProc) -> None:
    """Test select with custom tooltip."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_custom_tooltip")

    # Should have tooltip element
    tooltip = page.locator("#select_custom_tooltip_tooltip")
    expect(tooltip).to_be_attached()

    # Hover to show tooltip and verify text matches custom tooltip (not label)
    select_ctrl.loc_select.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_be_visible()
    expect(tooltip_content.first).to_contain_text("Change how items are displayed")
    # Verify it does NOT contain the label text
    expect(tooltip_content.first).not_to_contain_text("View mode")


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_no_tooltip(page: Page, app: ShinyAppProc) -> None:
    """Test select with tooltip disabled."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_no_tooltip")

    # Should NOT have a tooltip element
    tooltip = page.locator("#select_no_tooltip_tooltip")
    expect(tooltip).not_to_be_attached()

    # Hover should not show tooltip
    select_ctrl.loc_select.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content).not_to_be_visible()


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_grouped_choices(page: Page, app: ShinyAppProc) -> None:
    """Test select with grouped choices."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_grouped")
    expect(select_ctrl.loc_select).to_be_visible()

    # Check initial value (first option in first group)
    select_ctrl.expect_selected("a1")
    output = page.locator("#output_grouped")
    expect(output).to_have_text("Grouped select value: a1")

    # Should have optgroups
    optgroups = select_ctrl.loc_select.locator("optgroup")
    expect(optgroups).to_have_count(2)

    # Select from second group
    select_ctrl.set("b2")
    expect(output).to_have_text("Grouped select value: b2")

    # Should have default tooltip with label text (label hidden by default)
    tooltip = page.locator("#select_grouped_tooltip")
    expect(tooltip).to_be_attached()

    # Verify tooltip shows label text
    select_ctrl.loc_select.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_be_visible()
    expect(tooltip_content.first).to_contain_text("Select item")


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_update_choices(page: Page, app: ShinyAppProc) -> None:
    """Test updating select choices."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_update_choices")
    button = page.locator("#btn_update_choices")
    output = page.locator("#output_update_choices")

    # Initial choices: A, B, C
    select_ctrl.expect_selected("A")
    expect(output).to_have_text("Update choices value: A")

    # Click to update to X, Y, Z
    button.click()
    # "A" should still show as selected in the render.text even though it is no longer
    # in the choices because we have not selected a new value yet and we did not specify
    #  selected in the serverside update, so the input value retains its original
    expect(output).to_have_text("Update choices value: A")
    select_ctrl.expect_choices(["X", "Y", "Z"])

    # Click again to switch back to A, B, C with B selected
    button.click()
    # Now the selected value should change when options are updated because a selected
    # value was provided in the server update
    select_ctrl.expect_selected("B")
    expect(output).to_have_text("Update choices value: B")


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_update_selected(page: Page, app: ShinyAppProc) -> None:
    """Test updating selected value."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_update_selected")
    button = page.locator("#btn_update_selected")
    output = page.locator("#output_update_selected")

    # Initial: First
    select_ctrl.expect_selected("First")

    # Click to go to Second
    button.click()
    select_ctrl.expect_selected("Second")
    expect(output).to_have_text("Update selected value: Second")

    # Click to go to Third
    button.click()
    select_ctrl.expect_selected("Third")
    expect(output).to_have_text("Update selected value: Third")

    # Click to go back to First
    button.click()
    select_ctrl.expect_selected("First")
    expect(output).to_have_text("Update selected value: First")


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_update_label(page: Page, app: ShinyAppProc) -> None:
    """Test updating select label."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_update_label")
    button = page.locator("#btn_update_label")

    # Initial label
    expect(select_ctrl.loc_label).to_have_text("Initial Label")

    # Click to update
    button.click()
    expect(select_ctrl.loc_label).to_have_text("Updated 1")

    # Click again
    button.click()
    expect(select_ctrl.loc_label).to_have_text("Updated 2")


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_toggle_show_label(page: Page, app: ShinyAppProc) -> None:
    """Test toggling label visibility."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_toggle_show_label")
    button = page.locator("#btn_toggle_show_label")

    # Initially hidden
    expect(select_ctrl.loc_label).to_have_class(re.compile(r"visually-hidden"))

    # Click to show
    button.click()
    expect_not_to_have_class(select_ctrl.loc_label, "visually-hidden")

    # Click to hide again
    button.click()
    expect(select_ctrl.loc_label).to_have_class(re.compile(r"visually-hidden"))


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_update_icon(page: Page, app: ShinyAppProc) -> None:
    """Test updating select icon."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_update_icon")
    button = page.locator("#btn_update_icon")

    # Expect initial icon (sun)
    expect(select_ctrl.loc_icon.locator("svg")).to_have_attribute(
        "viewBox", "0 0 512 512"
    )

    # Click to update icon (to moon)
    button.click()

    expect(select_ctrl.loc_icon.locator("svg")).to_have_attribute(
        "viewBox", "0 0 384 512"
    )

    # Click again to toggle back to the original (sun)
    button.click()
    expect(select_ctrl.loc_icon.locator("svg")).to_have_attribute(
        "viewBox", "0 0 512 512"
    )


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_update_all(page: Page, app: ShinyAppProc) -> None:
    """Test updating all properties at once."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_update_all")
    output = page.locator("#output_update_all")

    # Initial state
    select_ctrl.expect_selected("Inactive")
    expect(select_ctrl.loc_label).to_have_text("Status")
    expect(select_ctrl.loc_label).to_have_class(re.compile(r"visually-hidden"))

    # Change selection to trigger update
    select_ctrl.set("Active")

    # After update: new label, new choices, new selected, icon added, label shown
    expect(select_ctrl.loc_label).to_have_text("New Status")
    expect_not_to_have_class(select_ctrl.loc_label, "visually-hidden")
    select_ctrl.expect_selected("Online")
    expect(output).to_have_text("Update all value: Online")

    # Icon should now be visible (was added by update)
    expect(select_ctrl.loc_icon).to_be_visible()
    # Verify the icon has an SVG element
    expect(select_ctrl.loc_icon.locator("svg")).to_be_visible()


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_icon_and_label(page: Page, app: ShinyAppProc) -> None:
    """Test select with both icon and label shown."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_icon_label")

    # Icon should be visible
    expect(select_ctrl.loc_icon).to_be_visible()

    # Label should be visible (not visually-hidden)
    expect(select_ctrl.loc_label).to_be_visible()
    expect_not_to_have_class(select_ctrl.loc_label, "visually-hidden")
    expect(select_ctrl.loc_label).to_have_text("Priority")

    # Should NOT have default tooltip when label is shown (even with icon)
    tooltip = page.locator("#select_icon_label_tooltip")
    expect(tooltip).not_to_be_attached()


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_custom_attributes(page: Page, app: ShinyAppProc) -> None:
    """Test select with custom attributes."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_custom_attr")
    expect(select_ctrl.loc).to_be_visible()

    # Should have custom data attributes
    expect(select_ctrl.loc).to_have_attribute("data-testid", "category-select")
    expect(select_ctrl.loc).to_have_attribute("style", "background-color: #f9b928;")

    # Select should still work
    select_ctrl.expect_selected("Tech")
    select_ctrl.set("Science")
    output = page.locator("#output_custom_attr")
    expect(output).to_have_text("Custom attr value: Science")


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_aria_attributes(page: Page, app: ShinyAppProc) -> None:
    """Test accessibility attributes."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_basic")

    # Label should have 'for' attribute pointing to select's id
    select_id = select_ctrl.loc_select.get_attribute("id")
    assert select_id is not None  # for type checking
    label_element = select_ctrl.loc.locator("label")
    expect(label_element).to_have_attribute("for", select_id)

    # Icon should be aria-hidden
    select_ctrl_icon = controller.ToolbarInputSelect(page, "select_icon")
    expect(select_ctrl_icon.loc_icon).to_have_attribute("aria-hidden", "true")


@pytest.mark.flaky(reruns=3)
def test_toolbar_select_structure(page: Page, app: ShinyAppProc) -> None:
    """Test the overall structure of toolbar_input_select."""
    page.goto(app.url)

    select_ctrl = controller.ToolbarInputSelect(page, "select_basic")

    # Should have the correct wrapper classes
    expect(select_ctrl.loc).to_have_class(
        re.compile(r"bslib-toolbar-input-select.*shiny-input-container")
    )

    # Should contain a label element
    label = select_ctrl.loc.locator("label")
    expect(label).to_be_attached()

    # Should contain a select element
    expect(select_ctrl.loc_select).to_be_attached()
    expect(select_ctrl.loc_select).to_have_class(
        re.compile(r"form-select.*bslib-toolbar-select")
    )
