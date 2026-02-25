import pytest
from conftest import create_app_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_app_fixture("./app.py")


@pytest.mark.flaky(reruns=3)
def test_numeric_input_toolbar_basic(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar in numeric input label - basic structure."""
    page.goto(app.url)

    # Find the numeric input using controller
    quantity = controller.InputNumeric(page, "quantity")
    quantity.expect_value("1")

    # Verify toolbar exists within the quantity input's container
    toolbar = quantity.loc_container.locator(".bslib-toolbar")
    expect(toolbar).to_be_visible()

    # Verify toolbar buttons exist using controllers
    btn_preset_10 = controller.ToolbarInputButton(page, "btn_preset_10")
    btn_preset_50 = controller.ToolbarInputButton(page, "btn_preset_50")
    btn_preset_100 = controller.ToolbarInputButton(page, "btn_preset_100")
    btn_reset = controller.ToolbarInputButton(page, "btn_reset")
    expect(btn_preset_10.loc).to_be_visible()
    expect(btn_preset_50.loc).to_be_visible()
    expect(btn_preset_100.loc).to_be_visible()
    expect(btn_reset.loc).to_be_visible()


@pytest.mark.flaky(reruns=3)
def test_numeric_input_toolbar_preset_buttons(page: Page, app: ShinyAppProc) -> None:
    """Test preset buttons functionality."""
    page.goto(app.url)

    quantity = controller.InputNumeric(page, "quantity")
    output = page.locator("#quantity_status")

    # Get toolbar button controllers
    btn_preset_10 = controller.ToolbarInputButton(page, "btn_preset_10")
    btn_preset_50 = controller.ToolbarInputButton(page, "btn_preset_50")
    btn_preset_100 = controller.ToolbarInputButton(page, "btn_preset_100")
    btn_reset = controller.ToolbarInputButton(page, "btn_reset")

    # Initial state
    quantity.expect_value("1")
    expect(output).to_contain_text("Quantity: 1")

    # Click preset 10
    btn_preset_10.click()
    quantity.expect_value("10")
    expect(output).to_contain_text("Quantity: 10")
    # Move cursor away and click elsewhere to unfocus and hide tooltip
    page.mouse.move(0, 0)
    page.mouse.click(0, 0)

    # Click preset 50
    btn_preset_50.click()
    quantity.expect_value("50")
    expect(output).to_contain_text("Quantity: 50")
    # Move cursor away and click elsewhere to unfocus and hide tooltip
    page.mouse.move(0, 0)
    page.mouse.click(0, 0)

    # Click preset 100
    btn_preset_100.click()
    quantity.expect_value("100")
    expect(output).to_contain_text("Quantity: 100")
    # Move cursor away and click elsewhere to unfocus and hide tooltip
    page.mouse.move(0, 0)
    page.mouse.click(0, 0)

    # Click reset
    btn_reset.click()
    quantity.expect_value("1")
    expect(output).to_contain_text("Quantity: 1")


@pytest.mark.flaky(reruns=3)
def test_numeric_input_toolbar_spacer(page: Page, app: ShinyAppProc) -> None:
    """Test that spacer pushes buttons to the right in numeric input toolbar."""
    page.goto(app.url)

    # Get toolbar button controllers
    btn_10 = controller.ToolbarInputButton(page, "btn_preset_10")
    btn_reset = controller.ToolbarInputButton(page, "btn_reset")

    # Buttons should be visible
    expect(btn_10.loc).to_be_visible()
    expect(btn_reset.loc).to_be_visible()

    # Get bounding boxes
    box_10 = btn_10.loc.bounding_box()
    box_reset = btn_reset.loc.bounding_box()

    assert box_10 is not None
    assert box_reset is not None

    # Reset button should be to the right of preset buttons
    # (spacer at the beginning pushes all buttons to the right as a group;
    # divider separates them but they're still adjacent)
    assert box_reset["x"] > box_10["x"] + box_10["width"]


@pytest.mark.flaky(reruns=3)
def test_text_area_toolbar_spacer_positioning(page: Page, app: ShinyAppProc) -> None:
    """Test that spacer creates proper spacing in text area toolbar."""
    page.goto(app.url)

    # Get select (before spacer) and clear button (after spacer) using controllers
    text_size = controller.ToolbarInputSelect(page, "text_size")
    btn_clear = controller.ToolbarInputButton(page, "btn_clear")

    # Both should be visible
    expect(text_size.loc).to_be_visible()
    expect(btn_clear.loc).to_be_visible()

    # Get bounding boxes
    select_box = text_size.loc.bounding_box()
    clear_box = btn_clear.loc.bounding_box()

    assert select_box is not None
    assert clear_box is not None

    # Clear button should be significantly to the right of select
    # Spacer creates gap between them
    assert clear_box["x"] > select_box["x"] + select_box["width"] + 20


@pytest.mark.flaky(reruns=3)
def test_submit_textarea_toolbar_positioning(page: Page, app: ShinyAppProc) -> None:
    """Test that toolbar has significant spacing before submit button."""
    page.goto(app.url)

    # Get copy button (last toolbar item) and submit button using controllers
    message = controller.InputSubmitTextarea(page, "message")
    btn_copy = controller.ToolbarInputButton(page, "btn_copy_draft")
    btn_submit = message.loc_button

    # Both should be visible
    expect(btn_copy.loc).to_be_visible()
    expect(btn_submit).to_be_visible()

    # Get bounding boxes
    copy_box = btn_copy.loc.bounding_box()
    submit_box = btn_submit.bounding_box()

    assert copy_box is not None
    assert submit_box is not None

    # Submit button should be significantly to the right of copy button
    assert submit_box["x"] > copy_box["x"] + copy_box["width"] + 20


@pytest.mark.flaky(reruns=3)
def test_text_area_toolbar_basic(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar in text area label - basic structure."""
    page.goto(app.url)

    # Find the text area using controller
    notes = controller.InputTextArea(page, "notes")
    expect(notes.loc).to_be_visible()

    # Verify toolbar exists within the notes textarea's container
    toolbar = notes.loc_container.locator(".bslib-toolbar")
    expect(toolbar).to_be_visible()

    # Verify toolbar buttons exist using controllers
    btn_bold = controller.ToolbarInputButton(page, "btn_bold")
    btn_italic = controller.ToolbarInputButton(page, "btn_italic")
    btn_link = controller.ToolbarInputButton(page, "btn_link")
    btn_clear = controller.ToolbarInputButton(page, "btn_clear")
    expect(btn_bold.loc).to_be_visible()
    expect(btn_italic.loc).to_be_visible()
    expect(btn_link.loc).to_be_visible()
    expect(btn_clear.loc).to_be_visible()

    # Verify toolbar select exists using controller
    text_size = controller.ToolbarInputSelect(page, "text_size")
    expect(text_size.loc).to_be_visible()


@pytest.mark.flaky(reruns=3)
def test_text_area_toolbar_clear_button(page: Page, app: ShinyAppProc) -> None:
    """Test clear button functionality."""
    page.goto(app.url)

    notes = controller.InputTextArea(page, "notes")
    btn_clear = controller.ToolbarInputButton(page, "btn_clear")

    # Type some text
    notes.set("Some test content")
    notes.expect_value("Some test content")

    # Click clear button
    btn_clear.click()

    # Text should be cleared
    notes.expect_value("")


@pytest.mark.flaky(reruns=3)
def test_text_area_toolbar_select(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar select functionality."""
    page.goto(app.url)

    text_size = controller.ToolbarInputSelect(page, "text_size")
    output = page.locator("#notes_status")

    # Initial value
    text_size.expect_selected("normal")
    expect(output).to_contain_text("Text Size: normal")

    # Change to small
    text_size.set("small")
    expect(output).to_contain_text("Text Size: small")

    # Change to large
    text_size.set("large")
    expect(output).to_contain_text("Text Size: large")


@pytest.mark.flaky(reruns=3)
def test_text_area_toolbar_button_clicks(page: Page, app: ShinyAppProc) -> None:
    """Test that toolbar buttons register clicks."""
    page.goto(app.url)

    output = page.locator("#notes_status")

    # Get toolbar button controllers
    btn_bold = controller.ToolbarInputButton(page, "btn_bold")
    btn_italic = controller.ToolbarInputButton(page, "btn_italic")
    btn_link = controller.ToolbarInputButton(page, "btn_link")

    # Wait for output to be ready
    expect(output).to_be_visible()

    # Initial state - all buttons have 0 clicks
    expect(output).to_contain_text("Bold: 0")
    expect(output).to_contain_text("Italic: 0")
    expect(output).to_contain_text("Link: 0")

    # Click bold button
    btn_bold.click()
    expect(output).to_contain_text("Bold: 1")
    # Move cursor away and click elsewhere to unfocus and hide tooltip
    page.mouse.move(0, 0)
    page.mouse.click(0, 0)

    # Click italic button
    btn_italic.click()
    expect(output).to_contain_text("Italic: 1")
    # Move cursor away and click elsewhere to unfocus and hide tooltip
    page.mouse.move(0, 0)
    page.mouse.click(0, 0)

    # Click link button
    btn_link.click()
    expect(output).to_contain_text("Link: 1")


@pytest.mark.flaky(reruns=3)
def test_submit_textarea_toolbar_basic(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar in submit textarea - basic structure."""
    page.goto(app.url)

    # Find the submit textarea using controller
    message = controller.InputSubmitTextarea(page, "message")
    expect(message.loc).to_be_visible()

    # Verify toolbar elements exist using controllers
    priority = controller.ToolbarInputSelect(page, "priority")
    btn_attach = controller.ToolbarInputButton(page, "btn_attach")
    btn_emoji = controller.ToolbarInputButton(page, "btn_emoji")
    btn_copy_draft = controller.ToolbarInputButton(page, "btn_copy_draft")
    expect(priority.loc).to_be_visible()
    expect(btn_attach.loc).to_be_visible()
    expect(btn_emoji.loc).to_be_visible()
    expect(btn_copy_draft.loc).to_be_visible()


@pytest.mark.flaky(reruns=3)
def test_submit_textarea_toolbar_select(page: Page, app: ShinyAppProc) -> None:
    """Test priority select functionality."""
    page.goto(app.url)

    priority = controller.ToolbarInputSelect(page, "priority")
    output = page.locator("#message_status")

    # Initial value
    priority.expect_selected("medium")
    expect(output).to_contain_text("Priority: medium")

    # Change to high
    priority.set("high")
    expect(output).to_contain_text("Priority: high")

    # Change to urgent
    priority.set("urgent")
    expect(output).to_contain_text("Priority: urgent")

    # Change to low
    priority.set("low")
    expect(output).to_contain_text("Priority: low")


@pytest.mark.flaky(reruns=3)
def test_submit_textarea_toolbar_buttons(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar buttons in submit textarea."""
    page.goto(app.url)

    output = page.locator("#message_status")

    # Get toolbar button controllers
    btn_attach = controller.ToolbarInputButton(page, "btn_attach")
    btn_emoji = controller.ToolbarInputButton(page, "btn_emoji")
    btn_copy_draft = controller.ToolbarInputButton(page, "btn_copy_draft")

    # Initial state - all buttons have 0 clicks
    expect(output).to_contain_text("Attach: 0")
    expect(output).to_contain_text("Emoji: 0")
    expect(output).to_contain_text("Copy: 0")

    # Click attach button
    btn_attach.click()
    expect(output).to_contain_text("Attach: 1")
    # Move cursor away and click elsewhere to unfocus and hide tooltip
    page.mouse.move(0, 0)
    page.mouse.click(0, 0)

    # Click emoji button
    btn_emoji.click()
    expect(output).to_contain_text("Emoji: 1")
    # Move cursor away and click elsewhere to unfocus and hide tooltip
    page.mouse.move(0, 0)
    page.mouse.click(0, 0)

    # Click copy button
    btn_copy_draft.click()
    expect(output).to_contain_text("Copy: 1")


@pytest.mark.flaky(reruns=3)
def test_submit_textarea_submit_functionality(page: Page, app: ShinyAppProc) -> None:
    """Test that submit button works."""
    page.goto(app.url)

    message = controller.InputSubmitTextarea(page, "message")
    output = page.locator("#message_status")

    # Initial state
    expect(output).to_contain_text("Submits: 0")

    # Type a message and submit
    message.set("Test message")
    message.loc_button.click()

    # Submit count should increment
    expect(output).to_contain_text("Submits: 1")


@pytest.mark.flaky(reruns=3)
def test_toolbar_dividers_present(page: Page, app: ShinyAppProc) -> None:
    """Test that toolbar dividers are present in all toolbars."""
    page.goto(app.url)

    # Test 1: Numeric input toolbar has divider
    quantity = controller.InputNumeric(page, "quantity")
    toolbar1 = quantity.loc_container.locator(".bslib-toolbar")
    divider1 = toolbar1.locator(".bslib-toolbar-divider")
    expect(divider1).to_have_count(1)

    # Test 2: Text area toolbar has divider
    notes = controller.InputTextArea(page, "notes")
    toolbar2 = notes.loc_container.locator(".bslib-toolbar")
    divider2 = toolbar2.locator(".bslib-toolbar-divider")
    expect(divider2).to_have_count(1)

    # Test 3: Submit textarea toolbar has divider
    # The toolbar elements are in the submit textarea's footer area
    # Count dividers near the submit textarea's toolbar buttons
    divider3 = (
        page.locator("#btn_attach")
        .locator("xpath=ancestor::div[contains(@class, 'bslib-toolbar')]")
        .locator(".bslib-toolbar-divider")
    )
    expect(divider3).to_have_count(1)


@pytest.mark.flaky(reruns=3)
def test_toolbar_spacers_present(page: Page, app: ShinyAppProc) -> None:
    """Test that toolbar spacers are present where expected."""
    page.goto(app.url)

    # Test 1: Numeric input toolbar has spacer
    quantity = controller.InputNumeric(page, "quantity")
    toolbar1 = quantity.loc_container.locator(".bslib-toolbar")
    spacer1 = toolbar1.locator(".bslib-toolbar-spacer")
    expect(spacer1).to_have_count(1)

    # Test 2: Text area toolbar has spacer
    notes = controller.InputTextArea(page, "notes")
    toolbar2 = notes.loc_container.locator(".bslib-toolbar")
    spacer2 = toolbar2.locator(".bslib-toolbar-spacer")
    expect(spacer2).to_have_count(1)
