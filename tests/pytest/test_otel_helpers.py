"""
Shared test utilities for OpenTelemetry tests.

Provides common helpers for setting up test isolation when working with
OpenTelemetry TracerProvider in tests.
"""

from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from shiny.otel._core import reset_otel_tracing_state


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
