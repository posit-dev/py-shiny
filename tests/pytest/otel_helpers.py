"""
Shared test utilities for OpenTelemetry tests.

Provides common helpers for setting up test isolation when working with
OpenTelemetry TracerProvider in tests.
"""

from contextlib import contextmanager
from typing import Iterator, Tuple, Union

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# Import internal globals for test manipulation
# These are imported directly to allow test isolation without going through public API
from shiny.otel import _core


def reset_otel_tracing_state() -> None:
    """
    Reset all cached OTel state to force re-evaluation.

    This clears the cached tracer and logger, forcing them to be re-evaluated
    on the next use. This is essential for test isolation, especially when
    setting up a new TracerProvider.

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

    Note: `is_otel_tracing_enabled()` no longer uses caching and will always
    reflect the current state of the TracerProvider.

    See Also
    --------
    patch_otel_tracing_state : Context manager to temporarily set tracing state
    """
    _core._tracer = None
    _core._logger = None


@contextmanager
def patch_otel_tracing_state(*, tracing_enabled: Union[bool, None]) -> Iterator[None]:
    """
    Context manager to temporarily set the tracing state for testing.

    This uses a test-only context variable to control what `is_otel_tracing_enabled()`
    returns, without manipulating the global TracerProvider. This approach works
    regardless of where or how the function is imported, eliminating the need to
    patch individual modules.

    Parameters
    ----------
    tracing_enabled
        The temporary value to set for tracing state. Can be True (enabled)
        or False (disabled). None is treated as False.

    Yields
    ------
    None

    Examples
    --------
    ```python
    from tests.pytest.otel_helpers import patch_otel_tracing_state
    from shiny.otel._core import is_otel_tracing_enabled
    from shiny.otel._collect import OtelCollectLevel, get_otel_collect_level

    # Test with tracing enabled
    with patch_otel_tracing_state(tracing_enabled=True):
        assert is_otel_tracing_enabled() is True
        # Can also check collect level
        assert get_otel_collect_level() >= OtelCollectLevel.SESSION

    # Test with tracing disabled
    with patch_otel_tracing_state(tracing_enabled=False):
        assert is_otel_tracing_enabled() is False
    ```

    Notes
    -----
    This is a test utility and should not be used in production code.
    The override is automatically cleared when exiting the context.

    Implementation detail: This works by setting a context variable that
    `is_otel_tracing_enabled()` checks before doing its normal provider detection.
    This is more robust than manipulating the TracerProvider because OpenTelemetry
    doesn't allow overriding providers once they're set.
    """
    enabled = bool(tracing_enabled)

    # Set the test override context variable
    token = _core._test_tracing_override.set(enabled)

    try:
        yield
    finally:
        # Restore the original value (None, meaning no override)
        _core._test_tracing_override.reset(token)


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


def otel_tracer_provider_impl() -> (
    Iterator[Tuple[TracerProvider, InMemorySpanExporter]]
):
    """
    Implementation for OpenTelemetry TracerProvider fixture.

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
    The exporter is automatically cleared before each test via the
    otel_tracer_provider fixture to ensure test isolation.
    Manual exporter.clear() calls are not needed.

    The original TracerProvider is saved and restored after the fixture
    completes to ensure proper cleanup.
    """
    # Save the original tracer provider
    original_provider = trace.get_tracer_provider()

    # Set up provider with in-memory exporter for testing
    memory_exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(memory_exporter))

    # Set this as the global tracer provider
    trace.set_tracer_provider(provider)

    # Reset tracing state to force re-evaluation with new provider
    reset_otel_tracing_state()

    yield provider, memory_exporter

    # Restore the original tracer provider
    trace.set_tracer_provider(original_provider)
    reset_otel_tracing_state()
