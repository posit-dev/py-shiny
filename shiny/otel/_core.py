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
    "reset_tracing_state",
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


def reset_tracing_state(tracing_enabled: Union[bool, None] = None) -> None:
    """
    Reset the cached tracing state.

    This function is primarily intended for testing purposes to allow tests to
    reset the global tracing state between test runs.

    Parameters
    ----------
    tracing_enabled
        Optional value to set for the tracing enabled state. If None (default),
        the state will be reset and will be re-evaluated on the next call to
        `is_otel_tracing_enabled()`. If True or False, sets an explicit value.

    Examples
    --------
    ```python
    # Reset to force re-evaluation
    reset_tracing_state()

    # Explicitly set to disabled for testing
    reset_tracing_state(False)

    # Explicitly set to enabled for testing
    reset_tracing_state(True)
    ```

    Notes
    -----
    This function is designed for test isolation and should generally not be
    used in production code. Tests should call this function to ensure a clean
    state between test runs.
    """
    global _tracing_enabled
    _tracing_enabled = tracing_enabled
