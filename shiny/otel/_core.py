"""Core OpenTelemetry infrastructure for lazy tracer and logger initialization."""

from __future__ import annotations

from typing import Any, Union

from opentelemetry import trace
from opentelemetry._logs import get_logger_provider
from opentelemetry.trace import Tracer

__all__ = (
    "get_otel_tracer",
    "get_otel_logger",
    "is_otel_tracing_enabled",
    "emit_log",
)

# Global state for lazy initialization
_tracer: Union[Tracer, None] = None
_logger: Union[Any, None] = None
_tracing_enabled: Union[bool, None] = None

# Tracer configuration
TRACER_NAME = "co.posit.python-package.shiny"


def get_otel_tracer() -> Tracer:
    """
    Get the OpenTelemetry tracer for Shiny, lazily initialized.

    The tracer is initialized on first use, allowing applications to configure
    OpenTelemetry before importing shiny modules.

    Returns
    -------
    Tracer
        The OpenTelemetry tracer instance for Shiny.
    """
    global _tracer
    if _tracer is None:
        # Import version dynamically to avoid circular import issues
        try:
            from .._version import __version__

            version = __version__
        except ImportError:
            version = "unknown"

        _tracer = trace.get_tracer(TRACER_NAME, version)
    return _tracer


def get_otel_logger() -> Any:  # type: ignore
    """
    Get the OpenTelemetry logger for Shiny, lazily initialized.

    Returns
    -------
    Logger
        The OpenTelemetry logger instance for Shiny.
    """
    global _logger
    if _logger is None:
        logger_provider = get_logger_provider()
        _logger = logger_provider.get_logger(TRACER_NAME)
    return _logger


def is_otel_tracing_enabled() -> bool:
    """
    Check if OpenTelemetry tracing is enabled.

    This checks whether the OTel SDK is properly configured by creating a test
    span and checking if it's recording. The result is cached to avoid repeated
    checks.

    Returns
    -------
    bool
        True if tracing is enabled, False otherwise.
    """
    global _tracing_enabled
    if _tracing_enabled is None:
        tracer = get_otel_tracer()
        # Check if spans are actually being recorded
        # When no SDK is configured, spans will be NonRecordingSpan instances
        with tracer.start_as_current_span("_otel_is_recording") as span:
            _tracing_enabled = span.is_recording()
    return _tracing_enabled


def emit_log(
    body: str,
    severity_text: str = "INFO",
    attributes: Union[dict[str, Any], None] = None,
) -> None:
    """
    Emit an OpenTelemetry log record.

    This function provides a simple interface for emitting structured log events
    to OpenTelemetry. It handles logger initialization and gracefully no-ops when
    OTel SDK is not configured.

    Parameters
    ----------
    body
        The log message body (main text of the log).
    severity_text
        The severity level of the log. Common values: "TRACE", "DEBUG", "INFO",
        "WARN", "ERROR", "FATAL". Defaults to "INFO".
    attributes
        Optional dictionary of attributes to attach to the log record.
        These provide additional structured context about the event.

    Examples
    --------
    ```python
    from shiny.otel._core import emit_log

    # Simple log message
    emit_log("Value updated")

    # Log with severity and attributes
    emit_log(
        "Set reactiveVal myValue",
        severity_text="DEBUG",
        attributes={"session.id": session_id, "value.name": "myValue"}
    )
    ```

    Notes
    -----
    This function is a no-op when the OTel SDK is not properly configured.
    No exceptions will be raised if logging fails.

    The function uses the OpenTelemetry Logs API, which follows the OpenTelemetry
    specification for log data model.
    """
    try:
        logger = get_otel_logger()
        logger.emit(
            body=body,
            severity_text=severity_text,
            attributes=attributes,
        )
    except Exception:
        # Silently fail if OTel logging is not configured or fails
        # We don't want telemetry issues to break the app
        pass
