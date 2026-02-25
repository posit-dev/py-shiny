"""
Test bookmark callbacks (on_restore and on_restored).

Verifies that:
1. on_restore is called before state is restored
2. on_restored is called after state is restored
3. Callbacks receive correct RestoreState
4. Callbacks are executed in the correct order
5. OTel spans are created for bookmark operations
"""

import json
import re
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, expect

from shiny.playwright.controller import InputActionButton, InputText, OutputCode
from shiny.run import ShinyAppProc


def test_bookmark_callbacks(page: Page, local_app: ShinyAppProc) -> None:
    """Test that on_restore and on_restored callbacks are called correctly."""

    # Navigate to clean URL without any bookmark state
    page.goto(local_app.url)

    # Wait for page to load
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

    # Wait for on_bookmark to appear in the log
    expect(callback_log.loc).to_contain_text("on_bookmark")
    expect(callback_log.loc).to_contain_text("on_bookmarked")

    # Wait for URL to be updated with bookmark
    expect(page).to_have_url(re.compile(r".*_inputs_.*"))

    # Reload page to trigger restore callbacks
    page.reload()

    # Wait for restore callbacks to appear in the log
    expect(callback_log.loc).to_contain_text("on_restore: text_input=modified_text")
    expect(callback_log.loc).to_contain_text("on_restored: text_input=modified_text")

    # Check that log contains the restore callbacks with correct value
    log_text_after = callback_log.loc.text_content()
    assert log_text_after is not None
    assert (
        "on_restore: text_input=modified_text" in log_text_after
    ), "Should have on_restore with modified_text"
    assert (
        "on_restored: text_input=modified_text" in log_text_after
    ), "Should have on_restored with modified_text"

    # Verify state was actually restored
    text_input.expect_value("modified_text")
    state_info.expect_value("Current text_input value: modified_text")


def test_bookmark_callbacks_order(page: Page, local_app: ShinyAppProc) -> None:
    """Test that callbacks are called in correct order during save and restore."""

    page.goto(local_app.url)

    text_input = InputText(page, "text_input")
    save_button = InputActionButton(page, "save_bookmark")
    callback_log = OutputCode(page, "callback_log")

    # Wait for initial page load
    expect(text_input.loc).to_have_count(1)

    # Test save sequence: on_bookmark -> on_bookmarked
    text_input.set("test_value")
    save_button.click()

    # Wait for bookmark callbacks to appear in the log
    expect(callback_log.loc).to_contain_text("on_bookmark")
    expect(callback_log.loc).to_contain_text("on_bookmarked")

    # Reload to test restore sequence: on_restore -> on_restored
    page.reload()

    # Wait for restore callbacks to appear in the log
    expect(callback_log.loc).to_contain_text("on_restore:")
    expect(callback_log.loc).to_contain_text("on_restored:")

    # After reload, log should have restore callbacks
    # Use locator to get text content
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


def test_bookmark_callbacks_otel_spans(page: Page, local_app: ShinyAppProc) -> None:
    """Test that OTel spans are created for bookmark operations."""

    page.goto(local_app.url)

    text_input = InputText(page, "text_input")
    save_button = InputActionButton(page, "save_bookmark")
    show_spans_button = InputActionButton(page, "show_spans")
    otel_spans_output = OutputCode(page, "otel_spans")

    # Change input and save bookmark
    text_input.set("otel_test_value")
    save_button.click()

    # Wait for URL to be updated with bookmark (confirms bookmark succeeded)
    expect(page).to_have_url(re.compile(r".*_inputs_.*"))

    # Click to show captured OTel spans
    show_spans_button.click()
    # Wait for actual JSON content (not just any non-empty content)
    expect(otel_spans_output.loc).to_contain_text('"name"')

    # Get the spans output and verify it contains span data
    spans_text = otel_spans_output.loc.text_content()
    print("Spans output text:", spans_text)
    assert spans_text is not None, "Spans output should have content"
    assert "error" not in spans_text.lower(), "Should not have OTel error"

    # Parse the JSON to verify structure
    spans_data: list[dict[str, Any]] = json.loads(spans_text)
    assert isinstance(spans_data, list), "Spans should be a list"
    assert len(spans_data) > 0, "Should have captured at least one span"

    # Verify span structure
    span_names: list[str] = [span["name"] for span in spans_data]
    print(f"Captured span names: {span_names}")

    # Should have session-related spans
    assert any(
        "session" in name.lower() for name in span_names
    ), "Should have session spans"

    # Reload to trigger restore callbacks
    page.reload()

    # Verify state was restored (this will wait for restore to complete)
    text_input.expect_value("otel_test_value")

    # Show spans again after restore
    show_spans_button.click()

    # Wait for spans to be processed and displayed (by checking that it contains valid JSON)
    expect(otel_spans_output.loc).not_to_contain_text(
        "Click 'Show OTel Spans' to view captured spans"
    )
    # Additional check to ensure JSON is actually present
    expect(otel_spans_output.loc).to_contain_text('"name"')

    # Verify we have more spans after restore
    spans_text_after = otel_spans_output.loc.text_content()
    assert spans_text_after is not None
    spans_data_after: list[dict[str, Any]] = json.loads(spans_text_after)

    # Should have at least as many spans as before (likely more)
    assert len(spans_data_after) >= len(
        spans_data
    ), "Should have accumulated spans after restore"

    span_names_after = [span["name"] for span in spans_data_after]
    print(f"Span names after restore: {span_names_after}")

    # Find bookmark-related spans (using underscore naming convention)
    restore_spans = [
        s for s in spans_data_after if s["name"] == "restore_bookmark_callbacks"
    ]
    restored_spans = [
        s for s in spans_data_after if s["name"] == "restored_bookmark_callbacks"
    ]

    assert len(restore_spans) > 0, "Should have 'restore_bookmark_callbacks' span"
    assert len(restored_spans) > 0, "Should have 'restored_bookmark_callbacks' span"

    # Get the most recent restore/restored spans (in case there are multiple from initial load)
    restore_span = restore_spans[-1]
    restored_span = restored_spans[-1]

    # Verify both spans have a parent
    assert (
        "parent_span_id" in restore_span
    ), "restore_bookmark_callbacks span should have a parent"
    assert (
        "parent_span_id" in restored_span
    ), "restored_bookmark_callbacks span should have a parent"

    # Build a lookup map of span_id to span
    span_lookup = {s["span_id"]: s for s in spans_data_after}

    # Find the parent spans
    restore_parent = span_lookup.get(restore_span["parent_span_id"])
    restored_parent = span_lookup.get(restored_span["parent_span_id"])

    # Verify parent spans exist and contain "reactive_update"
    assert (
        restore_parent is not None
    ), f"Should find parent for restore_bookmark_callbacks span (parent_id: {restore_span['parent_span_id']})"
    assert (
        restored_parent is not None
    ), f"Should find parent for restored_bookmark_callbacks span (parent_id: {restored_span['parent_span_id']})"

    assert (
        "reactive_update" in restore_parent["name"]
    ), f"restore_bookmark_callbacks parent should be reactive_update, got: {restore_parent['name']}"
    assert (
        "reactive_update" in restored_parent["name"]
    ), f"restored_bookmark_callbacks parent should be reactive_update, got: {restored_parent['name']}"

    # Verify timing: restore should start and end before restored starts
    assert (
        restore_span["start_time"] < restore_span["end_time"]
    ), "restore_bookmark_callbacks span should have valid timing"
    assert (
        restored_span["start_time"] < restored_span["end_time"]
    ), "restored_bookmark_callbacks span should have valid timing"
    assert (
        restore_span["end_time"] <= restored_span["start_time"]
    ), "restore_bookmark_callbacks should complete before restored_bookmark_callbacks starts"


def test_bookmark_callbacks_code_filepath(page: Page, local_app: ShinyAppProc) -> None:
    """Test that code.filepath attributes point to app code, not internal Shiny code."""

    page.goto(local_app.url)

    text_input = InputText(page, "text_input")
    save_button = InputActionButton(page, "save_bookmark")
    show_spans_button = InputActionButton(page, "show_spans")
    otel_spans_output = OutputCode(page, "otel_spans")

    # Change input and save bookmark
    text_input.set("filepath_test_value")
    save_button.click()

    # Wait for URL to be updated
    expect(page).to_have_url(re.compile(r".*_inputs_.*"))

    # Show captured spans before reload
    show_spans_button.click()
    # Wait for actual JSON content (not just any non-empty content)
    expect(otel_spans_output.loc).to_contain_text('"name"')

    spans_text = otel_spans_output.loc.text_content()
    print("Spans output text:", spans_text)
    assert spans_text is not None
    spans_before_reload: list[dict[str, Any]] = json.loads(spans_text)

    # Reload to trigger restore callbacks
    page.reload()
    text_input.expect_value("filepath_test_value")

    # Show spans after reload
    show_spans_button.click()
    expect(otel_spans_output.loc).not_to_contain_text(
        "Click 'Show OTel Spans' to view captured spans"
    )
    # Additional check to ensure JSON is actually present
    expect(otel_spans_output.loc).to_contain_text('"name"')

    spans_text_after = otel_spans_output.loc.text_content()
    assert spans_text_after is not None
    spans_after_reload: list[dict[str, Any]] = json.loads(spans_text_after)

    # Verify code.filepath for ALL spans
    all_spans = spans_before_reload + spans_after_reload
    spans_with_filepath = [
        s for s in all_spans if "code.filepath" in s.get("attributes", {})
    ]

    # Should have at least some spans with code.filepath
    assert (
        len(spans_with_filepath) > 0
    ), "Should have spans with code.filepath attribute"

    # Get the expected app directory (where the test app.py is located)
    test_dir = Path(__file__).parent.resolve()
    expected_app_file = test_dir / "app.py"

    # Verify code.filepath for all spans
    for span in spans_with_filepath:
        attrs = span["attributes"]
        filepath_str = attrs["code.filepath"]
        span_name = span["name"]

        # Convert to Path for robust cross-platform handling
        filepath = Path(filepath_str).resolve()

        # Verify the file exists
        assert filepath.exists(), (
            f"Span '{span_name}' has code.filepath pointing to non-existent file: "
            f"{filepath}"
        )

        # Verify it's NOT in internal Shiny library directories
        # Check if any parent directory is named 'shiny' with subdirs like 'bookmark', 'session', 'reactive'
        try:
            # Try to get relative path from shiny package location
            import shiny

            shiny_package_path = Path(shiny.__file__).parent.resolve()

            # Check if filepath is under the shiny package
            try:
                rel_path = filepath.relative_to(shiny_package_path)
                # If we get here, file is inside shiny package - check if it's in internal dirs
                internal_dirs = {"bookmark", "session", "reactive"}
                if rel_path.parts and rel_path.parts[0] in internal_dirs:
                    raise AssertionError(
                        f"Span '{span_name}' has code.filepath pointing to internal "
                        f"Shiny file in {rel_path.parts[0]}/: {filepath}"
                    )
            except ValueError:
                # filepath is not relative to shiny package - this is good
                pass
        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            # If we can't determine shiny package location, skip this check
            pass

        # Verify it's the expected app.py file
        assert filepath == expected_app_file, (
            f"Span '{span_name}' has code.filepath not pointing to test app.py. "
            f"Expected: {expected_app_file}, Got: {filepath}"
        )


# TODO: Additional test coverage for bookmark edge cases (Issue #8 from phase8_review.md)
#
# The following test scenarios would provide additional coverage but are deferred
# as optional enhancements. They are marked as "Suggestions (Non-Blocking)" in the
# Phase 8 review and can be implemented if specific issues arise:
#
# 1. Exception sanitization verification
#    - Test that exceptions in bookmark callbacks are sanitized
#    - Verify SafeException bypasses sanitization
#    - Confirm sensitive information (API keys, passwords) doesn't leak to UI
#    - Note: Error sanitization is already implemented in bookmark callbacks
#
# 2. Module namespacing compatibility
#    - Test bookmark callbacks work correctly in module proxy sessions
#    - Verify state restoration respects module namespaces
#    - Ensure callback registration works in nested module contexts
#
# 3. Concurrent bookmark operations
#    - Test concurrent bookmark.save() calls don't corrupt state
#    - Verify thread-safety of bookmark state updates
#    - Check for race conditions in state serialization
#
# 4. Async callback timeout handling
#    - Test slow async callbacks don't block flush cycle indefinitely
#    - Verify timeout behavior for long-running callbacks
#    - Ensure graceful degradation when callbacks exceed timeout
#
# These tests would require complex setup (module proxies, concurrent operation
# orchestration, timeout configuration) that exceeds the immediate value. The
# existing tests already cover the critical bookmark callback behaviors including
# ordering, state passing, and OTel instrumentation.
