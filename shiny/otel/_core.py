"""Core OpenTelemetry infrastructure for lazy tracer and logger initialization."""

from __future__ import annotations

from typing import Any, Union

from opentelemetry import trace
from opentelemetry._logs import get_logger_provider
from opentelemetry.trace import Tracer

from ._constants import TRACER_NAME

__all__ = (
    "get_otel_tracer",
    "get_otel_logger",
    "is_otel_tracing_enabled",
    "emit_otel_log",
)

# Global state for lazy initialization
_tracer: Union[Tracer, None] = None
_logger: Union[Any, None] = None
_tracing_enabled: Union[bool, None] = None


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

    This checks whether the OTel SDK is properly configured by examining if the
    tracer provider is a real SDK TracerProvider (not the no-op ProxyTracerProvider).
    The result is cached to avoid repeated checks.

    Returns
    -------
    bool
        True if tracing is enabled, False otherwise.
    """
    global _tracing_enabled
    if _tracing_enabled is None:
        try:
            from opentelemetry.sdk.trace import TracerProvider as SDKTracerProvider
        except (ImportError, ModuleNotFoundError):
            # opentelemetry-sdk is optional; if it's not available, tracing is disabled
            _tracing_enabled = False
        else:
            tracer_provider = trace.get_tracer_provider()
            # Check if we have a real SDK TracerProvider (not the no-op ProxyTracerProvider)
            # The SDK TracerProvider has span processors that record spans
            _tracing_enabled = isinstance(tracer_provider, SDKTracerProvider)
    return _tracing_enabled


def emit_otel_log(
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
    from shiny.otel._core import emit_otel_log

    # Simple log message
    emit_otel_log("Value updated")

    # Log with severity and attributes
    emit_otel_log(
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
