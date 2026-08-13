"""
Pytest configuration and fixtures for OpenTelemetry tests.
"""

from typing import Iterator, Tuple

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shiny.otel import _core
from shiny.otel._constants import TRACER_NAME

from .otel_helpers import otel_tracer_provider_impl


@pytest.fixture(scope="session")
def _otel_tracer_provider_session() -> (
    Iterator[Tuple[TracerProvider, InMemorySpanExporter]]
):
    """
    Internal session-scoped fixture for OpenTelemetry TracerProvider.

    Creates a single TracerProvider and InMemorySpanExporter for the entire test
    session. This is wrapped by the otel_tracer_provider fixture which provides
    automatic span clearing before each test.

    Why session-scoped?
    -------------------
    OpenTelemetry uses a global singleton for the tracer provider. Calling
    trace.set_tracer_provider() multiple times causes warnings and potential
    state corruption. Session scope ensures the provider is set once per
    pytest worker process, avoiding conflicts during parallel test execution.
    """
    yield from otel_tracer_provider_impl()


@pytest.fixture
def otel_tracer_provider(
    _otel_tracer_provider_session: Tuple[TracerProvider, InMemorySpanExporter],
) -> Iterator[Tuple[TracerProvider, InMemorySpanExporter]]:
    """
    Function-scoped pytest fixture for OpenTelemetry TracerProvider.

    Provides access to a session-scoped TracerProvider and InMemorySpanExporter,
    automatically clearing spans before each test to ensure test isolation.

    Why two fixtures instead of one?
    --------------------------------
    We cannot merge this into one function-scoped fixture because:
    1. The provider must be set globally once per worker (session scope)
    2. The exporter must be cleared per test (function scope)
    3. Creating new providers per test would repeatedly call
       trace.set_tracer_provider(), causing warnings and state corruption

    This two-fixture pattern separates the one-time global setup (session)
    from the per-test cleanup (function), working correctly with pytest-xdist.

    Why force `_core._tracer`?
    --------------------------
    `trace.set_tracer_provider()` is silently rejected when a provider was
    already installed in this worker process (e.g. by `test_otel_logfire.py`
    configuring logfire). In that case the session fixture's provider is not
    the global one, spans go somewhere else, and the in-memory exporter stays
    empty. Pointing Shiny's cached tracer at the test provider makes span
    assertions independent of which tests happen to share the worker. This
    mirrors what `test_otel_value_logging.py` does for `_core._logger`.

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
    # Force Shiny's cached tracer to come from the test provider, even if
    # `trace.set_tracer_provider()` was rejected because another test already
    # owned the global provider.
    _core._tracer = provider.get_tracer(TRACER_NAME)
    yield provider, exporter
    # Reset so subsequent callers re-fetch from the global provider
    _core._tracer = None
