"""High-level span creation helpers for async contexts."""

from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Callable, Dict, Iterator, Union

from opentelemetry.trace import Span, Status, StatusCode

from ._collect import OtelCollectLevel
from ._constants import ATTR_SESSION_ID

__all__ = ("with_otel_span", "with_otel_span_async")

# Type aliases for parameters
AttributesValue = Dict[str, Any] | None
AttributesType = Union[AttributesValue, Callable[[], AttributesValue]]
NameType = Union[str, Callable[[], str]]


@contextmanager
def with_otel_span(
    name: NameType,
    attributes: AttributesType = None,
    level: OtelCollectLevel = OtelCollectLevel.SESSION,
) -> Iterator[Span | None]:
    """
    Context manager for creating and managing an OpenTelemetry span.

    This is a synchronous version for non-async contexts. It automatically:
    - Checks if collection should occur based on the collection level
    - Creates a span with the given name and attributes (if collecting)
    - Records exceptions if they occur
    - Sets appropriate span status (OK or ERROR)
    - Ends the span when the context exits

    If collection is disabled or the SDK is not configured, this becomes a no-op
    context manager that yields None.

    Parameters
    ----------
    name
        The name of the span, or a callable that returns the span name. If a
        callable is provided, it will only be called if collection is enabled,
        allowing for lazy evaluation of expensive name generation.
    attributes
        Optional dictionary of attributes to attach to the span, or a callable
        that returns a dictionary. If a callable is provided, it will only be
        called if collection is enabled, allowing for lazy evaluation of
        expensive attribute extraction.
    level
        The minimum collection level required for this span. Defaults to SESSION.

    Yields
    ------
    Span | None
        The created span instance, or None if collection is disabled.

    Examples
    --------
    ```python
    from shiny.otel._span_wrappers import with_otel_span
    from shiny.otel import OtelCollectLevel

    # Static attributes
    with with_otel_span("my_operation", {"user_id": "123"}) as span:
        # Do work
        if span:
            span.set_attribute("result", "success")

    # Lazy attributes (only computed if collecting)
    with with_otel_span("session.start", lambda: extract_http_attributes(conn)) as span:
        # Attributes only extracted if span is created
        pass
    ```
    """
    from ._collect import should_otel_collect
    from ._core import get_otel_tracer

    if not should_otel_collect(level):
        yield None
        return

    # Resolve name if callable
    resolved_name = name() if callable(name) else name

    # Resolve attributes if callable
    resolved_attrs: Dict[str, Any] = {}
    if attributes is not None:
        if callable(attributes):
            resolved_attrs = attributes() or {}
        else:
            resolved_attrs = attributes

    tracer = get_otel_tracer()
    with tracer.start_as_current_span(
        resolved_name,
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


@asynccontextmanager
async def with_otel_span_async(
    name: NameType,
    attributes: AttributesType = None,
    level: OtelCollectLevel = OtelCollectLevel.SESSION,
) -> AsyncIterator[Span | None]:
    """
    Async context manager for creating and managing an OpenTelemetry span.

    This is the async version that properly propagates context through async
    boundaries. It automatically:
    - Checks if collection should occur based on the collection level
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
        The name of the span, or a callable that returns the span name. If a
        callable is provided, it will only be called if collection is enabled,
        allowing for lazy evaluation of expensive name generation.
    attributes
        Optional dictionary of attributes to attach to the span, or a callable
        that returns a dictionary. If a callable is provided, it will only be
        called if collection is enabled, allowing for lazy evaluation of
        expensive attribute extraction.
    level
        The minimum collection level required for this span. Defaults to SESSION.

    Yields
    ------
    Span | None
        The created span instance, or None if collection is disabled.

    Examples
    --------
    ```python
    from shiny.otel._span_wrappers import with_otel_span_async
    from shiny.otel import OtelCollectLevel

    async def my_async_function():
        # Static attributes
        async with with_otel_span_async("async_operation", {"count": 42}) as span:
            await some_async_call()
            if span:
                span.set_attribute("completed", True)

        # Lazy attributes (only computed if collecting)
        async with with_otel_span_async(
            "session.start",
            lambda: {ATTR_SESSION_ID: session.id, **extract_http_attributes(conn)}
        ) as span:
            # Attributes only extracted if span is created
            await session_work()
    ```
    """
    from ._collect import should_otel_collect
    from ._core import get_otel_tracer

    if not should_otel_collect(level):
        yield None
        return

    # Resolve name if callable
    resolved_name = name() if callable(name) else name

    # Resolve attributes if callable
    resolved_attrs: Dict[str, Any] = {}
    if attributes is not None:
        if callable(attributes):
            resolved_attrs = attributes() or {}
        else:
            resolved_attrs = attributes

    tracer = get_otel_tracer()
    with tracer.start_as_current_span(
        resolved_name,
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
