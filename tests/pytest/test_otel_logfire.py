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
"""

import pytest

from shiny.otel._core import is_otel_tracing_enabled

from .otel_helpers import reset_otel_tracing_state


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

    def test_logfire_provider_has_underlying_sdk_provider(self):
        """
        Test that logfire's ProxyTracerProvider wraps a real SDK TracerProvider.

        This verifies the underlying structure that our detection logic relies on.
        """
        try:
            import logfire
        except ImportError:
            pytest.skip("logfire not installed")

        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider as SDKTracerProvider

        # Configure logfire
        logfire.configure(token="test", send_to_logfire=False)

        # Get the provider
        tracer_provider = trace.get_tracer_provider()

        # Verify it's a proxy
        assert type(tracer_provider).__name__ == "ProxyTracerProvider"

        # Verify it has a .provider attribute
        assert hasattr(
            tracer_provider, "provider"
        ), "ProxyTracerProvider should have .provider attribute"

        # Verify the underlying provider is an SDK TracerProvider
        underlying = tracer_provider.provider  # type: ignore[attr-defined]
        assert isinstance(
            underlying, SDKTracerProvider
        ), "Underlying provider should be SDK TracerProvider"

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

    def test_no_provider_not_detected(self):
        """
        Test that when no provider is configured, OTel is correctly detected as disabled.
        """
        from opentelemetry import trace
        from opentelemetry.trace import ProxyTracerProvider

        # Reset to default (no-op) provider
        trace.set_tracer_provider(ProxyTracerProvider())

        # Reset cached state to force re-evaluation
        reset_otel_tracing_state()

        # Check that Shiny detects OTel is disabled
        assert (
            is_otel_tracing_enabled() is False
        ), "Shiny should not detect no-op provider as enabled"


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
