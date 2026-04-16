"""
Minimal Shiny Express app for testing session_start OTel span closure.

The OTel provider is configured in globals.py (runs once).  This file is
re-executed for every new session, but it only reads from the exporter —
it never replaces the TracerProvider.

On initial page load the span_summary output shows 0 session_start spans
because session_start hasn't ended yet (the initial flush runs inside it).
After clicking "Show Session Spans" the re-render fires outside session_start,
so the now-closed span is visible in the exporter.
"""

import json
import sys

from shiny import reactive
from shiny.express import input, render, ui

ui.page_opts(title="OTel Express Session Start Test")

ui.input_action_button("show_spans", "Show Session Spans")


"Logfire should only be configured once"


# globals.py is loaded once by create_express_app; access it via sys.modules
# so we always reference the same exporter even when this file is re-executed.
_globals = sys.modules["globals"]
_get_finished_spans = _globals.get_finished_spans


@render.code
@reactive.event(input.show_spans, ignore_none=False)
def span_summary():

    spans = _get_finished_spans()
    session_start_spans = [s for s in spans if s.name == "session_start"]

    info = {
        "session_start_count": len(session_start_spans),
        "all_closed": all(s.end_time is not None for s in session_start_spans),
        "session_start_spans": [
            {"name": s.name, "closed": s.end_time is not None}
            for s in session_start_spans
        ],
    }
    return json.dumps(info, indent=2)
