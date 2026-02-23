"""High-level span creation helpers for async contexts."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Callable, Dict, Mapping, Union

from opentelemetry.trace import Span, Status, StatusCode

from ._collect import OtelCollectLevel, get_otel_collect_level
from ._constants import ATTR_SESSION_ID
from ._core import get_otel_tracer, is_otel_tracing_enabled

__all__ = ("shiny_otel_span",)

# Type aliases for parameters
AttributesValue = Mapping[str, Any] | None
AttributesType = Union[AttributesValue, Callable[[], AttributesValue]]


@asynccontextmanager
async def shiny_otel_span(
    name: str,
    *,
    attributes: AttributesType = None,
    required_level: OtelCollectLevel = OtelCollectLevel.SESSION,
    collection_level: OtelCollectLevel | None = None,
) -> AsyncIterator[Span | None]:
    """
    Context manager for creating and managing a Shiny OpenTelemetry span.

    This async context manager properly propagates context through async
    boundaries. It automatically:
    - Checks if collection should occur based on the collect level
    - Creates a span with the given name and attributes (if collecting)
    - Records exceptions if they occur
    - Sets appropriate span status (OK or ERROR)
    - Ends the span when the context exits

    If collection is disabled or the SDK is not configured, this becomes a no-op
    context manager that yields None.

    Exception handling respects Shiny's error semantics:
    - Silent exceptions (SilentException, etc.) are not recorded in spans
    - Error messages are sanitized when app.sanitize_otel_errors is True
    - SafeException messages bypass sanitization

    Parameters
    ----------
    name
        The name of the span.
    attributes
        Optional dictionary of attributes to attach to the span, or a callable
        that returns a dictionary. If a callable is provided, it will only be
        called if collection is enabled, allowing for lazy evaluation of
        expensive attribute extraction.
    required_level
        The minimum collect level required for this span. Defaults to SESSION.

    Yields
    ------
    Span | None
        The created span instance, or None if collection is disabled.

    Examples
    --------
    ```python
    from shiny.otel._span_wrappers import shiny_otel_span

    async def my_async_function():
        # Static attributes
        async with shiny_otel_span("async_operation", attributes={"count": 42}) as span:
            await some_async_call()
            if span:
                span.set_attribute("completed", True)

        # Lazy attributes (only computed if collecting)
        async with shiny_otel_span(
            "session.start",
            attributes=lambda: {ATTR_SESSION_ID: session.id, **extract_http_attributes(conn)}
        ) as span:
            # Attributes only extracted if span is created
            await session_work()
    ```
    """
    # First check if OTel is enabled at all
    if not is_otel_tracing_enabled():
        yield None
        return

    # Use provided collection_level or get current level
    current_level = (
        collection_level if collection_level is not None else get_otel_collect_level()
    )

    # Check if we should collect based on current level vs required threshold
    if current_level < required_level:
        yield None
        return

    # Resolve attributes if callable
    resolved_attrs: Dict[str, Any] = {}
    if attributes is not None:
        if callable(attributes):
            attr_result = attributes()
            resolved_attrs = dict(attr_result) if attr_result else {}
        else:
            resolved_attrs = dict(attributes)

    tracer = get_otel_tracer()
    with tracer.start_as_current_span(
        name,
        attributes=resolved_attrs,
        record_exception=False,  # We handle exception recording manually
        set_status_on_exception=False,  # We handle status setting manually
    ) as span:
        try:
            yield span
            # If we reach here without exception, mark as OK
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            from ._errors import (
                has_otel_exception_been_recorded,
                is_silent_error,
                mark_otel_exception_as_recorded,
                maybe_sanitize_error,
            )

            # Check if this is a silent error
            if is_silent_error(e):
                # Silent errors don't set error status or record exceptions
                # Set status to OK since silent exceptions are not actual errors
                span.set_status(Status(StatusCode.OK))
            else:
                # Add session ID to span attributes if available
                from ..session import get_current_session

                session = get_current_session()
                if session is not None and hasattr(session, "id"):
                    span.set_attribute(ATTR_SESSION_ID, session.id)

                # Sanitize the error if needed before recording/setting status
                sanitized_exc = maybe_sanitize_error(e, session=session)

                # Only record the exception once at the innermost span where it originates
                # Parent spans will still get ERROR status, but won't duplicate the exception details
                if not has_otel_exception_been_recorded(e):
                    span.record_exception(sanitized_exc)
                    # Mark the original exception so parent spans don't record it again.
                    # Python propagates the same exception object when re-raising (not a copy),
                    # so this marking will be visible to all parent spans.
                    mark_otel_exception_as_recorded(e)

                # Always set error status on all spans that encounter the error
                span.set_status(Status(StatusCode.ERROR, str(sanitized_exc)))

            # Re-raise the original exception (not sanitized_exc) so the exception object
            # propagates unchanged to parent spans with the marking intact
            raise
