"""
Playwright test: session_start OTel span must be closed after the session starts.

The session_start span wraps server() + reactive_flush() during session init.
It must have a non-None end_time by the time any subsequent interaction can
fire — otherwise it appears as an "ongoing" span in backends such as Logfire.

This test specifically targets Shiny Express apps because express mode
re-executes the app module for each session (inside session_start), which can
cause TracerProvider replacement to interfere with span closure.
"""

from importlib.util import find_spec

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

    # Before clicking, the initial render fires inside session_start's
    # reactive_flush (before the span ends), so the count must be 0.
    expect(output.loc).to_contain_text('"session_start_count": 0,')

    # Click after page load so the re-render fires *outside* session_start.
    show_spans_btn.click()

    expect(output.loc).to_contain_text('"session_start_count": 1,')
    expect(output.loc).to_contain_text('"all_closed": true,')
