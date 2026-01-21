"""
Shared test utilities for OpenTelemetry tests.

Provides common helpers for setting up test isolation when working with
OpenTelemetry TracerProvider in tests.
"""

from contextlib import contextmanager
from typing import Iterator, Tuple, Union

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

# Import internal globals for test manipulation
# These are imported directly to allow test isolation without going through public API
from shiny.otel import _core


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
    _core._tracing_enabled = None
    _core._tracer = None
    _core._logger = None


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
    from tests.pytest.test_otel_helpers import patch_otel_tracing_state
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
    # Save original state
    original = _core._tracing_enabled
    try:
        # Set temporary state
        _core._tracing_enabled = tracing_enabled
        yield
    finally:
        # Restore original state
        _core._tracing_enabled = original


def get_exported_spans(provider: TracerProvider, exporter: InMemorySpanExporter):
    """
    Get exported spans from an InMemorySpanExporter with proper flushing.

    This helper ensures all spans are fully exported before returning them,
    which prevents race conditions in parallel test execution (pytest-xdist).

    Parameters
    ----------
    provider
        The TracerProvider that needs to be flushed.
    exporter
        The InMemorySpanExporter to get spans from.

    Returns
    -------
    list[ReadableSpan]
        List of exported spans, with internal OTel spans included.

    Examples
    --------
    ```python
    async def test_span_hierarchy(otel_tracer_provider):
        provider, exporter = otel_tracer_provider
        with patch_otel_tracing_state(tracing_enabled=True):
            # Create spans...
            pass

        # Get all exported spans with proper flushing
        spans = get_exported_spans(provider, exporter)
        app_spans = [s for s in spans if not s.name.startswith("_otel")]
        assert len(app_spans) > 0
    ```

    Notes
    -----
    Always call this helper instead of directly calling
    `exporter.get_finished_spans()` to ensure proper span flushing in
    parallel test execution environments.
    """
    # Force flush to ensure all spans are exported before checking
    # This prevents race conditions in parallel test execution
    provider.force_flush()

    # Get exported spans
    return exporter.get_finished_spans()


@pytest.fixture(scope="session")
def otel_tracer_provider() -> Iterator[Tuple[TracerProvider, InMemorySpanExporter]]:
    """
    Session-scoped pytest fixture for OpenTelemetry TracerProvider.

    Sets up a single InMemorySpanExporter and TracerProvider for all tests in the
    session. This avoids the complexity of manipulating OpenTelemetry internals
    and provides a reliable testing environment.

    The fixture is session-scoped to provide a single provider for all tests,
    which is more efficient and avoids issues with parallel test execution.

    Yields
    ------
    tuple[TracerProvider, InMemorySpanExporter]
        The provider and exporter for use in tests.

    Examples
    --------
    ```python
    async def test_span_hierarchy(otel_tracer_provider):
        provider, exporter = otel_tracer_provider
        with patch_otel_tracing_state(tracing_enabled=True):
            # Create spans...
            pass

        # Get exported spans with proper flushing
        spans = get_exported_spans(provider, exporter)
        assert len(spans) > 0
    ```

    Notes
    -----
    Tests should call exporter.clear() to clear spans between tests if needed.
    """
    # Set up provider with in-memory exporter for testing
    memory_exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(memory_exporter))

    # Set this as the global tracer provider
    trace.set_tracer_provider(provider)

    # Reset tracing state to force re-evaluation with new provider
    reset_otel_tracing_state()

    yield provider, memory_exporter

    # Cleanup is handled by pytest - no need to restore
