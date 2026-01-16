"""High-level span creation helpers for async contexts."""

from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Callable, Dict, Iterator, Union

from opentelemetry.trace import Span, Status, StatusCode

from ._collect import OtelCollectLevel

__all__ = ("with_otel_span", "with_otel_span_async")

# Type alias for attributes parameter
AttributesValue = Dict[str, Any] | None
AttributesType = Union[AttributesValue, Callable[[], AttributesValue]]


@contextmanager
def with_otel_span(
    name: str,
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
        The name of the span.
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

    # Resolve attributes if callable
    resolved_attrs: Dict[str, Any] = {}
    if attributes is not None:
        if callable(attributes):
            resolved_attrs = attributes() or {}
        else:
            resolved_attrs = attributes

    tracer = get_otel_tracer()
    with tracer.start_as_current_span(name, attributes=resolved_attrs) as span:
        try:
            yield span
            # If we reach here without exception, mark as OK
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            # Record the exception and set error status
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise


@asynccontextmanager
async def with_otel_span_async(
    name: str,
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

    Note: Exception recording and sanitization will be added in Phase 6.

    Parameters
    ----------
    name
        The name of the span.
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
            lambda: {"session.id": session.id, **extract_http_attributes(conn)}
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

    # Resolve attributes if callable
    resolved_attrs: Dict[str, Any] = {}
    if attributes is not None:
        if callable(attributes):
            resolved_attrs = attributes() or {}
        else:
            resolved_attrs = attributes

    tracer = get_otel_tracer()
    with tracer.start_as_current_span(name, attributes=resolved_attrs) as span:
        try:
            yield span
            # If we reach here without exception, mark as OK
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            # Record the exception and set error status
            # TODO: Phase 6 will add error sanitization here
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
