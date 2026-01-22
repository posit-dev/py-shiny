from conftest import ShinyAppProc, create_app_fixture
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_app_fixture("./app.py")


def test_toolbar_button_basic(page: Page, app: ShinyAppProc) -> None:
    """Test basic toolbar button functionality."""
    page.goto(app.url)

    # Test save button (icon-only)
    btn_save = controller.ToolbarInputButton(page, "btn_save")
    btn_save.expect_label("Save")
    btn_save.expect_icon(exists=True)
    btn_save.expect_label_visible(visible=False)  # Hidden for icon-only

    # Click and verify
    btn_save.click()
    output = controller.OutputText(page, "btn_save_value")
    output.expect_value("Save clicked: 1")

    # Click again
    btn_save.click()
    output.expect_value("Save clicked: 2")


def test_toolbar_button_with_label(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar button with both icon and label."""
    page.goto(app.url)

    btn_edit = controller.ToolbarInputButton(page, "btn_edit")
    btn_edit.expect_label("Edit")
    btn_edit.expect_icon(exists=True)
    btn_edit.expect_label_visible(visible=True)  # Visible when show_label=True

    btn_edit.click()
    output = controller.OutputText(page, "btn_edit_value")
    output.expect_value("Edit clicked: 1")


def test_toolbar_button_border(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar button with border."""
    page.goto(app.url)

    btn_delete = controller.ToolbarInputButton(page, "btn_delete")
    btn_delete.expect_border(has_border=True)

    btn_delete.click()
    output = controller.OutputText(page, "btn_delete_value")
    output.expect_value("Delete clicked: 1")


def test_toolbar_button_disabled(page: Page, app: ShinyAppProc) -> None:
    """Test disabled toolbar button."""
    page.goto(app.url)

    btn_disabled = controller.ToolbarInputButton(page, "btn_disabled")
    btn_disabled.expect_disabled(value=True)


def test_toolbar_select_basic(page: Page, app: ShinyAppProc) -> None:
    """Test basic toolbar select functionality."""
    page.goto(app.url)

    sel_filter = controller.ToolbarInputSelect(page, "sel_filter")
    sel_filter.expect_label("Filter")
    sel_filter.expect_icon(exists=True)
    sel_filter.expect_label_visible(visible=False)  # Hidden by default

    # Check initial selection (first choice)
    sel_filter.expect_selected("All")
    output = controller.OutputText(page, "sel_filter_value")
    output.expect_value("Filter: All")

    # Change selection
    sel_filter.set("Active")
    sel_filter.expect_selected("Active")
    output.expect_value("Filter: Active")

    # Change again
    sel_filter.set("Archived")
    sel_filter.expect_selected("Archived")
    output.expect_value("Filter: Archived")


def test_toolbar_select_with_label(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar select with visible label."""
    page.goto(app.url)

    sel_sort = controller.ToolbarInputSelect(page, "sel_sort")
    sel_sort.expect_label("Sort")
    sel_sort.expect_icon(exists=False)  # No icon
    sel_sort.expect_label_visible(visible=True)

    # Check initial selection (specified in app)
    sel_sort.expect_selected("date")
    output = controller.OutputText(page, "sel_sort_value")
    output.expect_value("Sort: date")

    # Change selection
    sel_sort.set("name")
    sel_sort.expect_selected("name")
    output.expect_value("Sort: name")


def test_toolbar_select_choices(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar select choices."""
    page.goto(app.url)

    sel_filter = controller.ToolbarInputSelect(page, "sel_filter")
    sel_filter.expect_choices(["All", "Active", "Archived"])


def test_update_toolbar_button(page: Page, app: ShinyAppProc) -> None:
    """Test updating toolbar button from server."""
    page.goto(app.url)

    btn_update = controller.ToolbarInputButton(page, "btn_update_me")
    btn_update.expect_label("Click to Update")
    btn_update.expect_icon(exists=True)

    # Click to trigger update
    btn_update.click()

    # Verify button was updated
    btn_update.expect_label("Updated!")
    # Icon should also be updated (though we can't easily check the icon content)
    btn_update.expect_icon(exists=True)

    # Click again to disable
    btn_update.click()
    btn_update.expect_disabled(value=True)


def test_update_toolbar_select(page: Page, app: ShinyAppProc) -> None:
    """Test updating toolbar select from server."""
    page.goto(app.url)

    sel_update = controller.ToolbarInputSelect(page, "sel_update_me")
    sel_update.expect_choices(["A", "B", "C"])
    sel_update.expect_selected("A")  # First choice by default

    # Click button to trigger update
    btn_update = controller.ToolbarInputButton(page, "btn_update_me")
    btn_update.click()

    # Verify select was updated with new choices and selection
    sel_update.expect_choices(["X", "Y", "Z"])
    sel_update.expect_selected("Y")


def test_toolbar_integration(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar with multiple elements working together."""
    page.goto(app.url)

    # Verify all buttons in first toolbar exist
    btn_save = controller.ToolbarInputButton(page, "btn_save")
    btn_edit = controller.ToolbarInputButton(page, "btn_edit")
    btn_delete = controller.ToolbarInputButton(page, "btn_delete")

    # Click each button and verify outputs update independently
    btn_save.click()
    controller.OutputText(page, "btn_save_value").expect_value("Save clicked: 1")
    controller.OutputText(page, "btn_edit_value").expect_value("Edit clicked: 0")

    btn_edit.click()
    controller.OutputText(page, "btn_save_value").expect_value("Save clicked: 1")
    controller.OutputText(page, "btn_edit_value").expect_value("Edit clicked: 1")

    btn_delete.click()
    controller.OutputText(page, "btn_delete_value").expect_value("Delete clicked: 1")


def test_toolbar_spacer_exists(page: Page, app: ShinyAppProc) -> None:
    """Test that toolbar spacer is present in the DOM."""
    page.goto(app.url)

    # Check that spacer exists with the correct class
    from playwright.sync_api import expect

    spacers = page.locator(".bslib-toolbar-spacer")
    expect(spacers).to_have_count(2)  # Two spacers in the app


def test_toolbar_spacer_basic(page: Page, app: ShinyAppProc) -> None:
    """Test basic toolbar spacer functionality."""
    page.goto(app.url)

    from playwright.sync_api import expect

    # Find the spacer toolbar
    toolbars = page.locator(".bslib-toolbar")
    spacer_toolbar = toolbars.nth(5)  # Sixth toolbar (Spacer Example)

    # Check spacer exists
    spacer = spacer_toolbar.locator(".bslib-toolbar-spacer")
    expect(spacer).to_have_count(1)
    expect(spacer).to_have_attribute("aria-hidden", "true")

    # Click buttons and verify they work
    btn_left = controller.ToolbarInputButton(page, "btn_spacer_left")
    btn_left.click()
    controller.OutputText(page, "btn_spacer_left_value").expect_value(
        "Left Side clicked: 1"
    )

    btn_right = controller.ToolbarInputButton(page, "btn_spacer_right")
    btn_right.click()
    controller.OutputText(page, "btn_spacer_right_value").expect_value(
        "Right Side clicked: 1"
    )


def test_toolbar_spacer_layout(page: Page, app: ShinyAppProc) -> None:
    """Test that spacer creates proper layout spacing."""
    page.goto(app.url)

    # Find the spacer toolbar
    toolbars = page.locator(".bslib-toolbar")
    spacer_toolbar = toolbars.nth(5)  # Sixth toolbar (Spacer Example)

    left_btn = spacer_toolbar.locator("#btn_spacer_left")
    right_btn = spacer_toolbar.locator("#btn_spacer_right")

    # Get bounding boxes
    left_box = left_btn.bounding_box()
    right_box = right_btn.bounding_box()

    # Buttons should be far apart (spacer pushes them to opposite ends)
    assert left_box is not None
    assert right_box is not None
    # Right button should be significantly to the right of left button
    assert right_box["x"] > left_box["x"] + 100


def test_toolbar_divider_and_spacer_combined(page: Page, app: ShinyAppProc) -> None:
    """Test combining toolbar_divider and toolbar_spacer."""
    page.goto(app.url)

    from playwright.sync_api import expect

    # Find the combination toolbar
    toolbars = page.locator(".bslib-toolbar")
    combo_toolbar = toolbars.nth(6)  # Seventh toolbar (Spacer + Divider)

    # Should have both divider and spacer
    divider = combo_toolbar.locator(".bslib-toolbar-divider")
    expect(divider).to_have_count(1)

    spacer = combo_toolbar.locator(".bslib-toolbar-spacer")
    expect(spacer).to_have_count(1)

    # Should have 4 buttons
    buttons = combo_toolbar.locator(".bslib-toolbar-input-button")
    expect(buttons).to_have_count(4)

    # Click buttons and verify they work
    btn1 = controller.ToolbarInputButton(page, "btn_combo_1")
    btn1.click()
    controller.OutputText(page, "btn_combo_1_value").expect_value("Undo clicked: 1")

    btn4 = controller.ToolbarInputButton(page, "btn_combo_4")
    btn4.click()
    controller.OutputText(page, "btn_combo_4_value").expect_value("Help clicked: 1")
