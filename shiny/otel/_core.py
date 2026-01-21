"""Core OpenTelemetry infrastructure for lazy tracer and logger initialization."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Union

from opentelemetry import trace
from opentelemetry._logs import get_logger_provider
from opentelemetry.trace import Tracer

__all__ = (
    "get_otel_tracer",
    "get_otel_logger",
    "is_otel_tracing_enabled",
    "reset_otel_tracing_state",
    "patch_otel_tracing_state",
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


def reset_otel_tracing_state() -> None:
    """
    Reset all cached OTel state to force re-evaluation.

    This clears the cached tracer, logger, and tracing enabled flag, forcing them
    to be re-evaluated on the next use. This is essential for test isolation,
    especially when setting up a new TracerProvider.

    Examples
    --------
    ```python
    # Reset all cached state between tests
    reset_otel_tracing_state()

    # Reset after setting up a new TracerProvider in tests
    trace.set_tracer_provider(new_provider)
    reset_otel_tracing_state()  # Force tracer to be re-fetched from new provider
    ```

    Notes
    -----
    This function is designed for test isolation and should generally not be
    used in production code. Tests should call this function to ensure a clean
    state between test runs.

    When setting up a new TracerProvider in tests, always call this function
    afterward to clear the cached tracer and force it to be re-fetched from
    the new provider. Otherwise, the old tracer from the previous provider
    will continue to be used.

    If you need to temporarily set specific values for testing, use the
    `patch_otel_tracing_state()` context manager instead.

    See Also
    --------
    patch_otel_tracing_state : Context manager to temporarily set tracing state
    """
    global _tracing_enabled, _tracer, _logger
    _tracing_enabled = None
    _tracer = None
    _logger = None


@contextmanager
def patch_otel_tracing_state(*, tracing_enabled: Union[bool, None]) -> Iterator[None]:
    """
    Context manager to temporarily patch the tracing state for testing.

    This provides a cleaner alternative to using `unittest.mock.patch` on
    the internal `_tracing_enabled` variable. It automatically saves and
    restores the original state.

    Parameters
    ----------
    tracing_enabled
        The temporary value to set for tracing state. Can be True (enabled),
        False (disabled), or None (uninitialized).

    Yields
    ------
    None

    Examples
    --------
    ```python
    from shiny.otel._core import patch_otel_tracing_state
    from shiny.otel import should_otel_collect, OtelCollectLevel

    # Test with tracing enabled
    with patch_otel_tracing_state(tracing_enabled=True):
        assert should_otel_collect(OtelCollectLevel.SESSION) is True

    # Test with tracing disabled
    with patch_otel_tracing_state(tracing_enabled=False):
        assert should_otel_collect(OtelCollectLevel.SESSION) is False
    ```

    Notes
    -----
    This is a test utility and should not be used in production code.
    The state is automatically restored when exiting the context.
    """
    global _tracing_enabled
    # Save original state
    original = _tracing_enabled
    try:
        # Set temporary state
        _tracing_enabled = tracing_enabled
        yield
    finally:
        # Restore original state
        _tracing_enabled = original
