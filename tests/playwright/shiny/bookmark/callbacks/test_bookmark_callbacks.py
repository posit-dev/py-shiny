"""
Test bookmark callbacks (on_restore and on_restored).

Verifies that:
1. on_restore and on_restored are called with correct RestoreState
2. Callbacks are executed in the correct order (on_restore before on_restored)
"""

import re

from playwright.sync_api import Page, expect

from shiny.playwright.controller import InputActionButton, InputText, OutputCode
from shiny.run import ShinyAppProc


def test_bookmark_callbacks(page: Page, local_app: ShinyAppProc) -> None:
    """Test that on_restore and on_restored callbacks are called correctly."""

    page.goto(local_app.url)
    page.wait_for_load_state("networkidle")

    text_input = InputText(page, "text_input")
    save_button = InputActionButton(page, "save_bookmark")
    callback_log = OutputCode(page, "callback_log")
    state_info = OutputCode(page, "restore_state_info")

    # Initial state
    text_input.expect_value("initial")
    state_info.expect_value("Current text_input value: initial")

    expect(text_input.loc).to_have_count(1)

    # Change input and save bookmark
    text_input.set("modified_text")
    state_info.expect_value("Current text_input value: modified_text")

    save_button.click()

    # Wait for bookmark callbacks to appear in the log
    expect(callback_log.loc).to_contain_text("on_bookmark")
    expect(callback_log.loc).to_contain_text("on_bookmarked")

    # Wait for URL to be updated with bookmark
    expect(page).to_have_url(re.compile(r".*_inputs_.*"))

    # Reload page to trigger restore callbacks
    page.reload()

    # Wait for restore callbacks to appear in the log
    expect(callback_log.loc).to_contain_text("on_restore: text_input=modified_text")
    expect(callback_log.loc).to_contain_text("on_restored: text_input=modified_text")

    # Verify state was actually restored
    text_input.expect_value("modified_text")
    state_info.expect_value("Current text_input value: modified_text")


def test_bookmark_callbacks_order(page: Page, local_app: ShinyAppProc) -> None:
    """Test that callbacks are called in correct order during save and restore."""

    page.goto(local_app.url)

    text_input = InputText(page, "text_input")
    save_button = InputActionButton(page, "save_bookmark")
    callback_log = OutputCode(page, "callback_log")

    expect(text_input.loc).to_have_count(1)

    # Save bookmark
    text_input.set("test_value")
    save_button.click()

    expect(callback_log.loc).to_contain_text("on_bookmark")
    expect(callback_log.loc).to_contain_text("on_bookmarked")

    # Reload to test restore sequence
    page.reload()

    expect(callback_log.loc).to_contain_text("on_restore:")
    expect(callback_log.loc).to_contain_text("on_restored:")

    log_text = callback_log.loc.text_content()
    assert log_text is not None, "Log should have content"
    lines = log_text.split("\n")

    # Check that on_restore comes before on_restored
    on_restore_idx = None
    on_restored_idx = None

    for i, line in enumerate(lines):
        if line.startswith("on_restore:"):
            on_restore_idx = i
        elif line.startswith("on_restored:"):
            on_restored_idx = i

    assert on_restore_idx is not None, "on_restore should be called"
    assert on_restored_idx is not None, "on_restored should be called"
    assert (
        on_restore_idx < on_restored_idx
    ), "on_restore should be called before on_restored"
