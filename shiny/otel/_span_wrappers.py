"""High-level span creation helpers for async contexts."""

from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Dict, Iterator, Optional

from opentelemetry.trace import Span, Status, StatusCode

__all__ = ("with_span", "with_span_async")


@contextmanager
def with_span(name: str, attributes: Optional[Dict[str, Any]] = None) -> Iterator[Span]:
    """
    Context manager for creating and managing an OpenTelemetry span.

    This is a synchronous version for non-async contexts. It automatically:
    - Creates a span with the given name and attributes
    - Records exceptions if they occur
    - Sets appropriate span status (OK or ERROR)
    - Ends the span when the context exits

    Parameters
    ----------
    name
        The name of the span.
    attributes
        Optional dictionary of attributes to attach to the span.

    Yields
    ------
    Span
        The created span instance.

    Examples
    --------
    ```python
    from shiny.otel._span_wrappers import with_span

    with with_span("my_operation", {"user_id": "123"}) as span:
        # Do work
        span.set_attribute("result", "success")
    ```
    """
    from ._core import get_tracer

    tracer = get_tracer()
    with tracer.start_as_current_span(name, attributes=attributes or {}) as span:
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
async def with_span_async(
    name: str, attributes: Optional[Dict[str, Any]] = None
) -> AsyncIterator[Span]:
    """
    Async context manager for creating and managing an OpenTelemetry span.

    This is the async version that properly propagates context through async
    boundaries. It automatically:
    - Creates a span with the given name and attributes
    - Records exceptions if they occur
    - Sets appropriate span status (OK or ERROR)
    - Ends the span when the context exits

    Note: Exception recording and sanitization will be added in Phase 6.

    Parameters
    ----------
    name
        The name of the span.
    attributes
        Optional dictionary of attributes to attach to the span.

    Yields
    ------
    Span
        The created span instance.

    Examples
    --------
    ```python
    from shiny.otel._span_wrappers import with_span_async

    async def my_async_function():
        async with with_span_async("async_operation", {"count": 42}) as span:
            # Do async work
            await some_async_call()
            span.set_attribute("completed", True)
    ```
    """
    from ._core import get_tracer

    tracer = get_tracer()
    with tracer.start_as_current_span(name, attributes=attributes or {}) as span:
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
