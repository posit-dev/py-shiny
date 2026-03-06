"""
OpenTelemetry Logfire Integration Tests

Tests cover:
- Detection of logfire's ProxyTracerProvider
- Correct identification of wrapped SDK TracerProvider
- Ensuring Shiny OTel instrumentation works with logfire

Background:
-----------
Logfire uses a ProxyTracerProvider that wraps an SDK TracerProvider. Prior to the
fix, Shiny's is_otel_tracing_enabled() only checked for direct SDKTracerProvider
instances using isinstance(), which returned False for logfire's proxy.

The fix (in shiny/otel/_core.py) now checks:
1. Direct SDKTracerProvider instances (original behavior)
2. Proxy providers with a .provider attribute that is an SDKTracerProvider (new)

This allows Shiny's built-in OTel instrumentation to work with logfire and other
tools that use proxy providers.

Note: logfire is an optional test dependency. Tests will skip if not installed.

IMPORTANT: These tests configure global OpenTelemetry providers that cannot be
overridden. They are marked with @pytest.mark.xdist_group to ensure they don't
run in parallel with other OTel tests to avoid interference.
"""

import pytest

from shiny.otel._core import is_otel_tracing_enabled

from .otel_helpers import reset_otel_tracing_state

pytestmark = pytest.mark.xdist_group(name="logfire_serial")


def _check_provider_not_already_set():
    """
    Check if OpenTelemetry providers are already configured.

    If providers are already set (e.g., by another test in parallel execution),
    skip the test to avoid "Overriding of current provider is not allowed" errors.
    """
    from opentelemetry import trace
    from opentelemetry._logs import get_logger_provider

    tracer_provider = trace.get_tracer_provider()
    logger_provider = get_logger_provider()

    # Check if real providers are already configured
    if hasattr(tracer_provider, "add_span_processor") and hasattr(
        logger_provider, "add_log_record_processor"
    ):
        pytest.skip(
            "OpenTelemetry providers already configured (likely by another test in parallel execution)"
        )


class TestLogfireIntegration:
    """Tests for logfire ProxyTracerProvider detection."""

    @pytest.fixture(autouse=True)
    def reset_state(self):
        """Reset OTel state before and after each test."""
        reset_otel_tracing_state()
        yield
        reset_otel_tracing_state()

    def test_logfire_proxy_provider_detected(self):
        """
        Test that is_otel_tracing_enabled() correctly detects logfire's ProxyTracerProvider.

        This test verifies the fix for issue where Shiny's OTel detection only
        recognized direct SDKTracerProvider instances, but logfire uses a
        ProxyTracerProvider that wraps an SDKTracerProvider.
        """
        _check_provider_not_already_set()

        try:
            import logfire
        except ImportError:
            pytest.skip("logfire not installed")

        # Configure logfire (with fake token for testing)
        logfire.configure(token="test", send_to_logfire=False)

        # Reset cached state to force re-evaluation
        reset_otel_tracing_state()

        # Check that Shiny detects OTel is enabled
        assert (
            is_otel_tracing_enabled() is True
        ), "Shiny should detect logfire's ProxyTracerProvider"

    def test_proxy_provider_with_underlying_sdk_detected(self):
        """
        Test that proxy providers with underlying SDK TracerProvider are detected.

        This tests our detection logic for wrapped providers (like logfire's
        ProxyTracerProvider) without depending on logfire's implementation.
        """
        _check_provider_not_already_set()

        from unittest.mock import Mock

        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider as SDKTracerProvider

        # Create a mock proxy provider that mimics logfire's structure
        mock_proxy_provider = Mock()
        mock_proxy_provider.provider = SDKTracerProvider()  # Wrapped SDK provider

        # Set as global provider
        trace.set_tracer_provider(mock_proxy_provider)
        reset_otel_tracing_state()

        # Verify our detection logic recognizes the proxy provider
        assert (
            is_otel_tracing_enabled() is True
        ), "Should detect proxy provider with underlying SDK TracerProvider"

    def test_direct_sdk_provider_still_detected(self):
        """
        Test that direct SDK TracerProvider instances are still detected.

        This ensures our fix didn't break the original detection logic.
        """
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
            InMemorySpanExporter,
        )

        # Set up a direct SDK TracerProvider (no proxy)
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(InMemorySpanExporter()))
        trace.set_tracer_provider(provider)

        # Reset cached state to force re-evaluation
        reset_otel_tracing_state()

        # Check that Shiny detects OTel is enabled
        assert (
            is_otel_tracing_enabled() is True
        ), "Shiny should detect direct SDK TracerProvider"


class TestLogfireSpanCreation:
    """Test that Shiny can create spans when logfire is configured."""

    @pytest.fixture(autouse=True)
    def reset_state(self):
        """Reset OTel state before and after each test."""
        reset_otel_tracing_state()
        yield
        reset_otel_tracing_state()

    def test_shiny_can_create_spans_with_logfire(self):
        """
        Test that Shiny can create OTel spans when logfire is configured.

        This is an integration test verifying the end-to-end flow works.
        """
        _check_provider_not_already_set()

        try:
            import logfire
        except ImportError:
            pytest.skip("logfire not installed")

        from shiny.otel._core import get_otel_tracer

        # Configure logfire
        logfire.configure(token="test", send_to_logfire=False)

        # Reset cached state to force re-evaluation
        reset_otel_tracing_state()

        # Get tracer (should use logfire's provider)
        tracer = get_otel_tracer()
        assert tracer is not None

        # Create a test span
        with tracer.start_as_current_span("test_span") as span:
            assert span is not None
            assert span.is_recording()
            span.set_attribute("test.key", "test.value")

        # If we got here without errors, span creation works
        assert True, "Successfully created span with logfire configured"
