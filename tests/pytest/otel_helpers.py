"""
Shared test utilities for OpenTelemetry tests.

Provides common helpers for setting up test isolation when working with
OpenTelemetry TracerProvider in tests.
"""

from contextlib import contextmanager
from typing import Iterator, Union

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


@contextmanager
def otel_tracer_provider_context():
    """
    Context manager for test isolation when using TracerProvider.

    Sets up an InMemorySpanExporter and TracerProvider, then restores
    the original provider on exit. This ensures tests don't interfere
    with each other when setting up their own tracing infrastructure.

    This is especially critical in CI environments with pytest-xdist where
    tests run in parallel and may have a global TracerProvider already set.

    Yields
    ------
    tuple[TracerProvider, InMemorySpanExporter]
        The provider and exporter for use in tests.

    Examples
    --------
    ```python
    async def test_span_hierarchy():
        with otel_tracer_provider_context() as (provider, exporter):
            with patch_otel_tracing_state(tracing_enabled=True):
                # Create spans...
                pass

            # Check exported spans
            spans = exporter.get_finished_spans()
            assert len(spans) > 0
    ```
    """
    # Save the current tracer provider to restore later
    old_provider = trace.get_tracer_provider()

    try:
        # Set up new provider with in-memory exporter
        memory_exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(memory_exporter))

        # Use internal API to force override for testing (needed for CI with pytest-xdist)
        trace._set_tracer_provider(provider, log=False)

        # Reset tracing state to force re-evaluation with new provider
        reset_otel_tracing_state()

        yield provider, memory_exporter
    finally:
        # Restore the original tracer provider
        trace._set_tracer_provider(old_provider, log=False)
        # Reset again to ensure clean state for next test
        reset_otel_tracing_state()
