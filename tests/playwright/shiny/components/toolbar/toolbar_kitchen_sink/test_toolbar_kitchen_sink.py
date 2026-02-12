import re

from conftest import create_app_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.playwright.expect import expect_not_to_have_class
from shiny.run import ShinyAppProc

app = create_app_fixture("./app.py")


def test_card1_header_toolbar(page: Page, app: ShinyAppProc) -> None:
    """Test Card 1: Toolbar in header with icon button, select, and divider."""
    page.goto(app.url)

    # Check save button (icon-only)
    btn_save = controller.ToolbarInputButton(page, "btn_save")
    expect(btn_save.loc).to_be_visible()
    expect(btn_save.loc_icon).to_be_visible()
    expect(btn_save.loc_label).to_have_attribute("hidden", "")

    # Check divider
    divider = page.locator(".bslib-toolbar-divider").first
    expect(divider).to_be_visible()
    expect(divider).to_have_attribute("aria-hidden", "true")

    # Check format select (label should be hidden by default)
    select_format = controller.ToolbarInputSelect(page, "format")
    expect(select_format.loc).to_be_visible()
    expect(select_format.loc_label).to_have_class(re.compile(r"visually-hidden"))


def test_card1_input_toolbar_label(page: Page, app: ShinyAppProc) -> None:
    """Test Card 1: Toolbar in input label with formatting buttons."""
    page.goto(app.url)

    # Check all three formatting buttons
    btn_bold = controller.ToolbarInputButton(page, "btn_bold")
    expect(btn_bold.loc).to_be_visible()
    expect(btn_bold.loc_icon).to_be_visible()

    btn_italic = controller.ToolbarInputButton(page, "btn_italic")
    expect(btn_italic.loc).to_be_visible()
    expect(btn_italic.loc_icon).to_be_visible()

    btn_code = controller.ToolbarInputButton(page, "btn_code")
    expect(btn_code.loc).to_be_visible()
    expect(btn_code.loc_icon).to_be_visible()

    # Verify textarea is present
    textarea = page.locator("#content")
    expect(textarea).to_be_visible()
    expect(textarea).to_have_attribute("placeholder", "Type your content here...")


def test_card1_interactions(page: Page, app: ShinyAppProc) -> None:
    """Test Card 1: Button clicks and select changes."""
    page.goto(app.url)

    output = page.locator("#output_card1")

    # Initial state
    expect(output).to_contain_text("Save: 0")
    expect(output).to_contain_text("Format: md")
    expect(output).to_contain_text("Bold: 0")

    # Click save button
    btn_save = controller.ToolbarInputButton(page, "btn_save")
    btn_save.click()
    expect(output).to_contain_text("Save: 1")

    # Change format
    select_format = controller.ToolbarInputSelect(page, "format")
    select_format.set("html")
    expect(output).to_contain_text("Format: html")

    # Click formatting buttons
    btn_bold = controller.ToolbarInputButton(page, "btn_bold")
    btn_bold.click()
    expect(output).to_contain_text("Bold: 1")

    btn_italic = controller.ToolbarInputButton(page, "btn_italic")
    btn_italic.click()
    btn_italic.click()
    expect(output).to_contain_text("Italic: 2")


def test_card2_header_toolbar(page: Page, app: ShinyAppProc) -> None:
    """Test Card 2: Toolbar in header with label button, spacer, and select with label."""
    page.goto(app.url)

    # Check new button (icon and label visible)
    btn_new = controller.ToolbarInputButton(page, "btn_new")
    expect(btn_new.loc).to_be_visible()
    expect(btn_new.loc_icon).to_be_visible()
    expect(btn_new.loc_label).to_be_visible()
    expect(btn_new.loc_label).to_have_text("New Message")
    expect(btn_new.loc).to_have_attribute("data-type", "both")

    # Check spacer exists (spacers are not visually "visible", they just take up space)
    spacer = page.locator(".bslib-toolbar-spacer")
    expect(spacer).to_be_attached()
    expect(spacer).to_have_attribute("aria-hidden", "true")

    # Check recipient select with visible label
    select_recipient = controller.ToolbarInputSelect(page, "recipient")
    expect(select_recipient.loc).to_be_visible()
    # Label should be visible (not have visually-hidden class)
    expect_not_to_have_class(select_recipient.loc_label, "visually-hidden")
    expect(select_recipient.loc_label).to_be_visible()
    expect(select_recipient.loc_label).to_have_text("To")


def test_card2_submit_textarea_toolbar(page: Page, app: ShinyAppProc) -> None:
    """Test Card 2: Submit textarea with toolbar parameter."""
    page.goto(app.url)

    # Check priority select
    select_priority = controller.ToolbarInputSelect(page, "priority")
    expect(select_priority.loc).to_be_visible()
    expect(select_priority.loc_icon).to_be_visible()

    # Check divider in textarea toolbar
    dividers = page.locator(".bslib-toolbar-divider")
    expect(dividers.nth(1)).to_be_visible()  # Second divider (first is in card 1)

    # Check attach and emoji buttons
    btn_attach = controller.ToolbarInputButton(page, "btn_attach")
    expect(btn_attach.loc).to_be_visible()

    btn_emoji = controller.ToolbarInputButton(page, "btn_emoji")
    expect(btn_emoji.loc).to_be_visible()

    # Verify submit textarea is present
    textarea = page.locator("#message")
    expect(textarea).to_be_visible()
    expect(textarea).to_have_attribute("placeholder", "Compose your message...")


def test_card2_interactions(page: Page, app: ShinyAppProc) -> None:
    """Test Card 2: Button clicks, select changes, and submit."""
    page.goto(app.url)

    output = page.locator("#output_card2")

    # Initial state
    expect(output).to_contain_text("New: 0")
    expect(output).to_contain_text("To: team")
    expect(output).to_contain_text("Priority: medium")
    expect(output).to_contain_text("Submits: 0")

    # Click new button
    btn_new = controller.ToolbarInputButton(page, "btn_new")
    btn_new.click()
    expect(output).to_contain_text("New: 1")

    # Change recipient
    select_recipient = controller.ToolbarInputSelect(page, "recipient")
    select_recipient.set("manager")
    expect(output).to_contain_text("To: manager")

    # Change priority
    select_priority = controller.ToolbarInputSelect(page, "priority")
    select_priority.set("high")
    expect(output).to_contain_text("Priority: high")

    # Click toolbar buttons
    btn_attach = controller.ToolbarInputButton(page, "btn_attach")
    btn_attach.click()
    expect(output).to_contain_text("Attach: 1")

    btn_emoji = controller.ToolbarInputButton(page, "btn_emoji")
    btn_emoji.click()
    btn_emoji.click()
    expect(output).to_contain_text("Emoji: 2")

    # Submit message
    message_input = controller.InputSubmitTextarea(page, "message")
    message_input.set("Test message content")

    # Click the submit button using controller
    message_input.loc_button.click()
    expect(output).to_contain_text("Submits: 1")


def test_all_toolbar_elements_present(page: Page, app: ShinyAppProc) -> None:
    """Test that all toolbar element types are present and functional."""
    page.goto(app.url)

    # Verify all button elements are present using controllers
    btn_save = controller.ToolbarInputButton(page, "btn_save")
    expect(btn_save.loc).to_be_visible()

    btn_bold = controller.ToolbarInputButton(page, "btn_bold")
    expect(btn_bold.loc).to_be_visible()

    btn_italic = controller.ToolbarInputButton(page, "btn_italic")
    expect(btn_italic.loc).to_be_visible()

    btn_code = controller.ToolbarInputButton(page, "btn_code")
    expect(btn_code.loc).to_be_visible()

    btn_new = controller.ToolbarInputButton(page, "btn_new")
    expect(btn_new.loc).to_be_visible()

    btn_attach = controller.ToolbarInputButton(page, "btn_attach")
    expect(btn_attach.loc).to_be_visible()

    btn_emoji = controller.ToolbarInputButton(page, "btn_emoji")
    expect(btn_emoji.loc).to_be_visible()

    # Verify all select elements are present using controllers
    select_format = controller.ToolbarInputSelect(page, "format")
    expect(select_format.loc).to_be_visible()

    select_recipient = controller.ToolbarInputSelect(page, "recipient")
    expect(select_recipient.loc).to_be_visible()

    select_priority = controller.ToolbarInputSelect(page, "priority")
    expect(select_priority.loc).to_be_visible()

    # Verify dividers are present
    dividers = page.locator(".bslib-toolbar-divider")
    expect(dividers.first).to_be_visible()
    expect(dividers.nth(1)).to_be_visible()

    # Verify spacer is present (spacers are not visually "visible", they just take up space)
    spacer = page.locator(".bslib-toolbar-spacer")
    expect(spacer).to_be_attached()


def test_toolbar_alignment(page: Page, app: ShinyAppProc) -> None:
    """Test that all toolbars have correct alignment."""
    page.goto(app.url)

    # All toolbars in this app should be right-aligned
    # Only check toolbars that have data-align attribute (actual ui.toolbar() elements)
    toolbars = page.locator(".bslib-toolbar[data-align]")
    count = toolbars.count()
    for i in range(count):
        toolbar = toolbars.nth(i)
        expect(toolbar).to_have_attribute("data-align", "right")


def test_tooltips_on_icon_only_buttons(page: Page, app: ShinyAppProc) -> None:
    """Test that icon-only buttons have tooltips."""
    page.goto(app.url)

    # Icon-only buttons should have tooltips
    icon_only_buttons = [
        "btn_save",
        "btn_bold",
        "btn_italic",
        "btn_code",
        "btn_attach",
        "btn_emoji",
    ]

    for btn_id in icon_only_buttons:
        tooltip = page.locator(f"#{btn_id}_tooltip")
        expect(tooltip).to_be_attached()


def test_no_tooltips_on_label_buttons(page: Page, app: ShinyAppProc) -> None:
    """Test that buttons with visible labels don't have tooltips by default."""
    page.goto(app.url)

    # Button with visible label should not have tooltip
    tooltip = page.locator("#btn_new_tooltip")
    expect(tooltip).not_to_be_attached()


def test_update_tooltip_after_update_button(page: Page, app: ShinyAppProc) -> None:
    """Test updating tooltip content after updating toolbar button."""
    page.goto(app.url)

    btn_save = controller.ToolbarInputButton(page, "btn_save")
    tooltip = page.locator("#btn_save_tooltip")

    # Verify initial tooltip exists
    expect(tooltip).to_be_attached()

    # Hover to show initial tooltip
    btn_save.loc.hover()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).to_be_visible()
    expect(tooltip_content.first).to_contain_text("Save Document")

    # Move away to hide tooltip
    page.mouse.move(0, 0)
    expect(tooltip_content.first).not_to_be_visible()

    # Click button to trigger update_toolbar_input_button and update_tooltip
    btn_save.click()
    page.mouse.move(0, 0)

    # Wait for icon to change to circle-check (viewBox for circle-check icon)
    # This ensures the button update has been processed
    expect(btn_save.loc_icon.locator("svg")).to_have_attribute("viewBox", "0 0 512 512")

    # Click elsewhere to ensure any open tooltip is closed
    page.locator("h2").click()
    tooltip_content = page.locator(".tooltip-inner")
    expect(tooltip_content.first).not_to_be_visible()

    # Now hover to show the updated tooltip
    btn_save.loc.hover()

    # Wait for the tooltip to show the new text
    expect(tooltip_content.first).to_be_visible()
    expect(tooltip_content.first).to_contain_text("Saved successfully!")
    # Verify it no longer shows the old tooltip
    expect(tooltip_content.first).not_to_contain_text("Save Document")
