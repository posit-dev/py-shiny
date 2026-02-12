"""
Pytest configuration and fixtures for OpenTelemetry tests.
"""

from typing import Iterator, Tuple

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from .otel_helpers import otel_tracer_provider_impl


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
    yield from otel_tracer_provider_impl()
