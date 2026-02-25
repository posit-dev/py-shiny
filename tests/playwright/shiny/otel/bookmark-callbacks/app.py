"""
Test app for bookmark callbacks (on_restore and on_restored).

This app tracks when callbacks are invoked to verify they execute
in the correct order during bookmark restoration. It also captures
and displays OpenTelemetry spans.
"""

import json
import os

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.bookmark import RestoreState
from shiny.bookmark._save_state import BookmarkState

os.environ["SHINY_OTEL_COLLECT"] = "all"

# Set up OTel span collection if SHINY_OTEL_COLLECT is enabled
_span_exporter = None
_tracer_provider = None

if os.environ.get("SHINY_OTEL_COLLECT"):
    from opentelemetry import trace
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    _span_exporter = InMemorySpanExporter()
    _tracer_provider = TracerProvider()
    _tracer_provider.add_span_processor(SimpleSpanProcessor(_span_exporter))
    trace.set_tracer_provider(_tracer_provider)


def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_text("text_input", "Enter text:", value="initial"),
        ui.input_action_button("save_bookmark", "Save Bookmark"),
        ui.input_action_button("show_spans", "Show OTel Spans"),
        ui.hr(),
        ui.h4("Callback Log:"),
        ui.output_code("callback_log"),
        ui.h4("Current State:"),
        ui.output_code("restore_state_info"),
        ui.h4("OTel Spans:"),
        ui.output_code("otel_spans"),
    )


def server(input: Inputs, output: Outputs, session: Session):
    from typing import Any

    # Track callback invocations
    callback_log_data: reactive.Value[list[str]] = reactive.value([])
    spans_data: reactive.Value[list[dict[str, Any]] | dict[str, Any] | None] = (
        reactive.value(None)
    )

    @reactive.effect
    @reactive.event(input.save_bookmark)
    async def _():
        await session.bookmark()

    @reactive.effect
    @reactive.event(input.show_spans)
    def _():
        if _span_exporter is None:
            spans_data.set({"error": "OTel not enabled. Set SHINY_OTEL_COLLECT=all"})
            return

        # Get all spans from the exporter
        spans = _span_exporter.get_finished_spans()

        # Convert spans to a readable format
        spans_info: list[dict[str, Any]] = []
        for span in spans:
            # Get span ID from context
            span_id = f"{span.context.span_id:016x}" if span.context else "unknown"

            span_dict = {
                "name": span.name,
                "span_id": span_id,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "status": {
                    "status_code": str(span.status.status_code),
                },
                "attributes": dict(span.attributes) if span.attributes else {},
            }
            # Add parent info if it exists
            if span.parent:
                span_dict["parent_span_id"] = f"{span.parent.span_id:016x}"

            spans_info.append(span_dict)

        spans_data.set(spans_info)

    @session.bookmark.on_bookmark
    async def _(state: BookmarkState):
        log = callback_log_data()
        new_log = log + ["on_bookmark"]  # Create new list to trigger reactivity
        callback_log_data.set(new_log)

    @session.bookmark.on_bookmarked
    async def _(url: str):
        log = callback_log_data()
        new_log = log + ["on_bookmarked"]  # Create new list to trigger reactivity
        callback_log_data.set(new_log)
        await session.bookmark.update_query_string(url)

    @session.bookmark.on_restore
    def _(state: RestoreState):
        log = callback_log_data()
        new_log = log + [
            f"on_restore: text_input={state.input.get('text_input', 'N/A')}"
        ]  # Create new list
        callback_log_data.set(new_log)

    @session.bookmark.on_restored
    def _(state: RestoreState):
        log = callback_log_data()
        new_log = log + [
            f"on_restored: text_input={state.input.get('text_input', 'N/A')}"
        ]  # Create new list
        callback_log_data.set(new_log)

    @render.code
    def callback_log():
        return "\n".join(callback_log_data())

    @render.code
    def restore_state_info():
        # Show current input value
        return f"Current text_input value: {input.text_input()}"

    @render.code
    def otel_spans():
        data = spans_data()
        if data is None:
            return "Click 'Show OTel Spans' to view captured spans"
        return json.dumps(data, indent=2, default=str)


app = App(app_ui, server, bookmark_store="url")
