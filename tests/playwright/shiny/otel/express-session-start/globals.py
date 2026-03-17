"""
OTel setup — executed ONCE at app startup, not re-run per session.

Express apps re-execute their app.py for every new session (inside the
session_start span), so any module-level code in app.py that calls
trace.set_tracer_provider() would replace the provider *while* session_start
is open.  Placing setup here in globals.py avoids that: Shiny loads this file
a single time before the first session starts.

Call ``get_finished_spans()`` from app.py to retrieve captured spans.
"""

import os
from typing import cast

import logfire
from logfire.testing import TestExporter
from opentelemetry import trace
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

os.environ["SHINY_OTEL_COLLECT"] = "reactivity"

_span_exporter = TestExporter()

logfire.configure(
    service_name="shiny-otel-express-session-test",
    scrubbing=False,
)
cast(TracerProvider, trace.get_tracer_provider()).add_span_processor(
    SimpleSpanProcessor(_span_exporter)
)


def get_finished_spans() -> list[ReadableSpan]:
    """Return all finished spans captured by logfire's TestExporter."""
    return list(_span_exporter.exported_spans)


def clear_spans() -> None:
    """Clear all captured spans. Call once per session to reset the counter."""
    _span_exporter.clear()
