"""
Playwright test: session_start OTel span must be closed after the session starts.

The session_start span wraps server() + reactive_flush() during session init.
It must have a non-None end_time by the time any subsequent interaction can
fire — otherwise it appears as an "ongoing" span in backends such as Logfire.

This test specifically targets Shiny Express apps because express mode
re-executes the app module for each session (inside session_start), which can
cause TracerProvider replacement to interfere with span closure.
"""

import json
from importlib.util import find_spec
from typing import Any

import pytest
from playwright.sync_api import Page, expect

from shiny.playwright.controller import InputActionButton, OutputCode
from shiny.run import ShinyAppProc


@pytest.mark.skipif(find_spec("logfire") is None, reason="logfire is not installed")
def test_session_start_span_closes(page: Page, local_app: ShinyAppProc) -> None:
    """session_start span must be closed (have end_time) after the session starts."""
    page.goto(local_app.url)

    show_spans_btn = InputActionButton(page, "show_spans")
    output = OutputCode(page, "span_summary")

    # Click after page load so the re-render fires *outside* session_start.
    # (The initial render runs inside session_start's reactive_flush, before
    # the span has ended, so session_start_count would be 0 on first render.)
    show_spans_btn.click()

    # Wait for the output to reflect at least one session_start span.
    expect(output.loc).to_contain_text("session_start")

    raw = output.loc.text_content()
    assert raw is not None, "span_summary output must not be None"

    data: dict[str, Any] = json.loads(raw)

    assert data["session_start_count"] >= 1, (
        f"Expected at least one session_start span, got {data['session_start_count']}. "
        f"Full output: {raw}"
    )

    assert data["all_closed"] is True, (
        "One or more session_start spans have no end_time — they were never closed. "
        f"Full output: {raw}"
    )
