"""Core OpenTelemetry infrastructure for lazy tracer and logger initialization."""

from __future__ import annotations

import contextlib
from contextvars import ContextVar
from typing import Any, Generator, Union

from opentelemetry import context as otel_context
from opentelemetry import trace

# There is no public API for get_logger_provider.
# Use private module, similar to logfire: https://github.com/pydantic/logfire/blob/ac3f23b5c03675d6c0f95e037f2a5eab0420f09d/logfire/_internal/logs.py#L11
from opentelemetry._logs import get_logger_provider
from opentelemetry.trace import Tracer

from ._constants import ATTR_SESSION_ID, TRACER_NAME

__all__ = (
    "get_otel_tracer",
    "get_otel_logger",
    "is_otel_tracing_enabled",
    "emit_otel_log",
    "detached_otel_context",
)

# Global state for lazy initialization
_tracer: Union[Tracer, None] = None
_logger: Union[Any, None] = None

# Test-only override for is_otel_tracing_enabled()
# This is used by test helpers to control tracing state without manipulating
# the global TracerProvider (which OpenTelemetry doesn't allow after setup)
_test_tracing_override: ContextVar[Union[bool, None]] = ContextVar(
    "test_tracing_override", default=None
)


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
    tracer provider is a real SDK TracerProvider (or a proxy wrapping one).

    This function checks the current state on every call, allowing users to set up
    their TracerProvider after importing Shiny.

    Returns
    -------
    bool
        True if tracing is enabled, False otherwise.
    """
    # Check for test-only override first (used by test helpers)
    test_override = _test_tracing_override.get()
    if test_override is not None:
        return test_override

    # Note: This function does not cache its result to allow users to set up their
    # TracerProvider after importing Shiny. The performance impact is negligible
    # (~0.22μs per check), and the check only happens when creating spans.
    try:
        from opentelemetry.sdk.trace import TracerProvider as SDKTracerProvider
    except ImportError:
        # If we can't import the SDK TracerProvider, tracing is disabled
        return False

    tracer_provider = trace.get_tracer_provider()

    # Check if we have a real SDK TracerProvider
    if isinstance(tracer_provider, SDKTracerProvider):
        return True

    # Also check for proxy providers (e.g., logfire's ProxyTracerProvider)
    # that wrap an SDK TracerProvider
    if hasattr(tracer_provider, "provider") and isinstance(
        tracer_provider.provider,  # type: ignore[attr-defined]
        SDKTracerProvider,
    ):
        return True

    return False


def emit_otel_log(
    body: str,
    severity_text: str = "INFO",
    attributes: Union[dict[str, Any], None] = None,
    *,
    infer_session_id: bool,
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
    infer_session_id
        If ``True``, automatically add ``session.id`` from current
        session context when not provided in ``attributes``. Set to ``False``
        to opt out of automatic inference.

    Examples
    --------
    ```python
    from shiny.otel._core import emit_otel_log

    # Simple log message
    emit_otel_log("Value updated")

    # Log with severity and attributes
    emit_otel_log(
        "Set reactive.value myValue",
        severity_text="DEBUG",
        attributes={"session.id": session_id, "value.name": "myValue"},
        infer_session_id=True,  # Automatically add session.id if not provided
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
        # Auto-add session.id if not already present and a session is available.
        # This works because session.id is consistent across sessions and modules
        # (a SessionProxy shares the same id as its parent AppSession).
        resolved_attrs = dict(attributes) if attributes else {}
        if infer_session_id and ATTR_SESSION_ID not in resolved_attrs:
            from ..session._utils import get_current_session

            session = get_current_session()
            if session is not None and hasattr(session, "id"):
                resolved_attrs[ATTR_SESSION_ID] = session.id

        logger = get_otel_logger()
        logger.emit(
            body=body,
            severity_text=severity_text,
            attributes=resolved_attrs if resolved_attrs else None,
        )
    except Exception:
        # Silently fail if OTel logging is not configured or fails
        # We don't want telemetry issues to break the app
        pass


@contextlib.contextmanager
def detached_otel_context() -> Generator[None, None, None]:
    """
    Context manager that detaches from the current OpenTelemetry span context.

    Any spans created within this block will appear as root spans (no parent).
    This is useful for timer-driven work that is not causally related to any
    ongoing user action — for example, a ``reactive.poll`` flush that fires
    independently of the request/response cycle.

    Examples
    --------
    ```python
    from shiny.otel._core import detached_otel_context

    with detached_otel_context():
        ctx.invalidate()
        await flush()
    ```
    """
    token = otel_context.attach(otel_context.Context())
    try:
        yield
    finally:
        otel_context.detach(token)
