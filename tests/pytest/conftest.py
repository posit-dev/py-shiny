"""
Pytest configuration and fixtures for OpenTelemetry tests.
"""

from typing import Iterator, Tuple

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from .otel_helpers import otel_tracer_provider_impl


@pytest.fixture(scope="session")
def _otel_tracer_provider_session() -> Iterator[Tuple[TracerProvider, InMemorySpanExporter]]:
    """
    Internal session-scoped fixture for OpenTelemetry TracerProvider.

    Creates a single TracerProvider and InMemorySpanExporter for the entire test
    session. This is wrapped by the otel_tracer_provider fixture which provides
    automatic span clearing before each test.
    """
    yield from otel_tracer_provider_impl()


@pytest.fixture
def otel_tracer_provider(
    _otel_tracer_provider_session: Tuple[TracerProvider, InMemorySpanExporter]
) -> Tuple[TracerProvider, InMemorySpanExporter]:
    """
    Function-scoped pytest fixture for OpenTelemetry TracerProvider.

    Provides access to a session-scoped TracerProvider and InMemorySpanExporter,
    automatically clearing spans before each test to ensure test isolation.

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
    The exporter is automatically cleared before each test for isolation.
    Manual exporter.clear() calls are not needed.
    """
    provider, exporter = _otel_tracer_provider_session
    # Clear spans from previous tests to ensure isolation
    exporter.clear()
    return provider, exporter
