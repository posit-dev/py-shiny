"""
Test that input values and client data are NOT logged by OTel.

Verifies that:
1. No input value logs are emitted on initial app load
2. No client data logs are emitted on initial app load
3. Input and client data accesses do NOT generate OTel logs (by design)

This behavior is intentional - input.* and .clientData values are filtered
out from OTel logging to reduce noise, as documented in shiny/reactive/_reactives.py.
Only user-created reactive.Value() objects emit value update logs.
"""

import json
from typing import Any

from playwright.sync_api import Page, expect

from shiny.playwright.controller import InputActionButton, OutputCode
from shiny.run import ShinyAppProc


def test_no_input_clientdata_logs_on_load(page: Page, local_app: ShinyAppProc) -> None:
    """Test that no input/client data logs are emitted on initial load."""

    page.goto(local_app.url)

    show_logs_button = InputActionButton(page, "show_logs")
    otel_logs_output = OutputCode(page, "otel_logs")

    # Immediately check logs after page load
    show_logs_button.click()

    # Wait for logs to be displayed
    expect(otel_logs_output.loc).not_to_contain_text("Click 'Show OTel Logs'")
    # Also check that it contains valid JSON (at minimum "[]")
    expect(otel_logs_output.loc).to_contain_text("[")

    # Get the logs
    logs_text = otel_logs_output.loc.text_content()
    assert logs_text is not None, "Logs output should not be None"
    assert (
        logs_text.strip() != ""
    ), f"Logs output should not be empty, got: '{logs_text}'"

    # Parse the logs
    logs_data: list[dict[str, Any]] = json.loads(logs_text)

    # Filter to logs that mention input or clientdata
    input_clientdata_logs = [
        log
        for log in logs_data
        if "input." in str(log.get("body", "")).lower()
        or "clientdata" in str(log.get("body", "")).lower()
        or any(
            "input." in str(v).lower() or "clientdata" in str(v).lower()
            for v in log.get("attributes", {}).values()
        )
    ]

    # Should have NO input/clientdata logs on initial load
    assert (
        len(input_clientdata_logs) == 0
    ), f"Should have no input/clientdata logs on initial load, found {len(input_clientdata_logs)}"


def test_no_input_clientdata_logs_after_access(
    page: Page, local_app: ShinyAppProc
) -> None:
    """Test that input/client data accesses do NOT generate logs (by design)."""

    page.goto(local_app.url)

    access_button = InputActionButton(page, "access_values")
    show_logs_button = InputActionButton(page, "show_logs")
    otel_logs_output = OutputCode(page, "otel_logs")
    accessed_values_output = OutputCode(page, "accessed_values")

    # Get baseline log count
    show_logs_button.click()
    expect(otel_logs_output.loc).not_to_contain_text("Click 'Show OTel Logs'")
    # Also check that it contains valid JSON (at minimum "[]")
    expect(otel_logs_output.loc).to_contain_text("[")

    initial_logs_text = otel_logs_output.loc.text_content()
    assert initial_logs_text is not None
    initial_logs: list[dict[str, Any]] = json.loads(initial_logs_text)

    # Access input and client data values
    access_button.click()

    # Verify values were accessed
    expect(accessed_values_output.loc).to_contain_text("text_input")
    expect(accessed_values_output.loc).to_contain_text("url_protocol")

    # Check logs after access
    show_logs_button.click()
    expect(otel_logs_output.loc).not_to_contain_text("Click 'Show OTel Logs'")
    # Also check that it contains valid JSON (at minimum "[]")
    expect(otel_logs_output.loc).to_contain_text("[")

    final_logs_text = otel_logs_output.loc.text_content()
    assert final_logs_text is not None
    final_logs: list[dict[str, Any]] = json.loads(final_logs_text)

    # Filter for input/clientdata related logs
    initial_input_logs = [
        log
        for log in initial_logs
        if "input." in str(log).lower() or "clientdata" in str(log).lower()
    ]
    final_input_logs = [
        log
        for log in final_logs
        if "input." in str(log).lower() or "clientdata" in str(log).lower()
    ]

    # Should still have NO input/clientdata logs after access
    # This is by design - input.* and .clientData values are filtered from logging
    assert (
        len(initial_input_logs) == 0
    ), f"Should have no input logs initially, found {len(initial_input_logs)}"
    assert (
        len(final_input_logs) == 0
    ), f"Should have no input logs after access (filtered by design), found {len(final_input_logs)}"

    print(
        "\n\u2713 Verified: input.* and .clientData values are not logged (by design)"
    )
    print(f"  Total logs before access: {len(initial_logs)}")
    print(f"  Total logs after access: {len(final_logs)}")
