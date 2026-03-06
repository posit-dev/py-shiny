"""
Test app for client data and input initialization value logging.

This app verifies that initial input values and client data are NOT logged
on app initialization, but ARE logged when explicitly accessed after load.
"""

import json
import os

from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import InMemoryLogRecordExporter
from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

os.environ["SHINY_OTEL_COLLECT"] = "all"

# Set up OTel log collection
_log_exporter = None
_logger_provider = None

if os.environ.get("SHINY_OTEL_COLLECT"):
    from opentelemetry import _logs
    from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor

    _log_exporter = InMemoryLogRecordExporter()
    _logger_provider = LoggerProvider()
    _logger_provider.add_log_record_processor(SimpleLogRecordProcessor(_log_exporter))
    _logs.set_logger_provider(_logger_provider)


def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_text("text_input", "Enter text:", value="initial_text"),
        ui.input_slider("slider_input", "Select value:", min=0, max=100, value=50),
        ui.input_action_button("access_values", "Access Input/Client Values"),
        ui.input_action_button("show_logs", "Show OTel Logs"),
        ui.hr(),
        ui.h4("Accessed Values:"),
        ui.output_code("accessed_values"),
        ui.h4("OTel Logs:"),
        ui.output_code("otel_logs"),
    )


def server(input: Inputs, output: Outputs, session: Session):
    from typing import Any

    # Track accessed values
    accessed_data: reactive.Value[dict[str, Any]] = reactive.Value({})
    logs_data: reactive.Value[list[dict[str, Any]] | dict[str, Any] | None] = (
        reactive.Value(None)
    )

    @reactive.effect
    @reactive.event(input.access_values)
    def _():
        # Access inputs and client data - this should generate logs
        values = {
            "text_input": input.text_input(),
            "slider_input": input.slider_input(),
            "url_protocol": session.clientdata.url_protocol(),
            "url_hostname": session.clientdata.url_hostname(),
            "url_port": session.clientdata.url_port(),
        }
        accessed_data.set(values)

    @reactive.effect
    @reactive.event(input.show_logs)
    def _():
        if _log_exporter is None:
            logs_data.set({"error": "OTel not enabled. Set SHINY_OTEL_COLLECT=all"})
            return

        # Get all logs from the exporter
        log_records = _log_exporter.get_finished_logs()

        # Convert logs to a readable format
        logs_info: list[dict[str, Any]] = []
        for log_record in log_records:
            log_dict = {
                "body": str(log_record.log_record.body),
                "severity_text": log_record.log_record.severity_text,
                "attributes": (
                    dict(log_record.log_record.attributes)
                    if log_record.log_record.attributes
                    else {}
                ),
                "timestamp": log_record.log_record.timestamp,
            }
            logs_info.append(log_dict)

        logs_data.set(logs_info)

    @render.code
    def accessed_values():
        data = accessed_data()
        if not data:
            return "Click 'Access Input/Client Values' to access values"
        return json.dumps(data, indent=2)

    @render.code
    def otel_logs():
        data = logs_data()
        if data is None:
            return "Click 'Show OTel Logs' to view captured logs"
        return json.dumps(data, indent=2, default=str)


app = App(app_ui, server)
