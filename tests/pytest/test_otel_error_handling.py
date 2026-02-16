"""
OpenTelemetry Error Handling and Sanitization

Tests cover:
- Silent error detection
- Error sanitization based on app settings
- SafeException bypass
- Exception recording in spans
- Span status on errors
"""

# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode

from shiny import App
from shiny.otel._errors import (
    is_silent_error,
    maybe_sanitize_error,
    should_sanitize_errors,
)
from shiny.session import Session, session_context
from shiny.types import SafeException, SilentCancelOutputException, SilentException

from .otel_helpers import get_exported_spans, patch_otel_tracing_state


@pytest.fixture(scope="function")  # Changed to function scope for test isolation
def otel_tracer_provider():
    """Set up OpenTelemetry TracerProvider for testing."""
    from opentelemetry import trace

    from .otel_helpers import reset_otel_tracing_state

    # Create in-memory exporter and tracer provider
    memory_exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(memory_exporter))

    # Set as global tracer provider
    trace.set_tracer_provider(provider)

    # Reset OTel state to pick up new provider
    reset_otel_tracing_state()

    # Clear any existing spans
    memory_exporter.clear()

    yield provider, memory_exporter

    # Cleanup is handled by pytest


@pytest.fixture
def mock_session():
    """Create a mock session for testing."""
    from unittest.mock import Mock

    from shiny._namespaces import ResolvedId

    session = Mock(spec=Session)
    session.id = "test-session-123"
    session.ns = ResolvedId("")  # Root namespace

    # Create a mock app with sanitize_otel_errors settings
    app = Mock(spec=App)
    app.sanitize_errors = False  # UI error sanitization
    app.sanitize_otel_errors = True  # OTel error sanitization (default)
    app.sanitize_error_msg = "An error has occurred. Check your logs or contact the app author for clarification."
    session.app = app

    return session


class TestSilentErrorDetection:
    """Tests for is_silent_error() function"""

    def test_silent_exception_is_detected(self):
        """Test that SilentException is detected as silent"""
        exc = SilentException("This should be silent")
        assert is_silent_error(exc) is True

    def test_silent_cancel_output_exception_is_detected(self):
        """Test that SilentCancelOutputException is detected as silent"""
        exc = SilentCancelOutputException("Cancel but keep output")
        assert is_silent_error(exc) is True

    def test_silent_operation_in_progress_is_detected(self):
        """Test that SilentOperationInProgressException is detected as silent"""
        from shiny.types import SilentOperationInProgressException

        exc = SilentOperationInProgressException("Operation in progress")
        assert is_silent_error(exc) is True

    def test_regular_exception_is_not_silent(self):
        """Test that regular exceptions are not detected as silent"""
        exc = ValueError("This is a regular error")
        assert is_silent_error(exc) is False

    def test_safe_exception_is_not_silent(self):
        """Test that SafeException is not silent (should be recorded)"""
        exc = SafeException("This is safe to show")
        assert is_silent_error(exc) is False


class TestErrorSanitization:
    """Tests for error sanitization logic"""

    def test_should_sanitize_with_flag_enabled(self, mock_session):
        """Test that sanitization is enabled when app setting is True"""
        mock_session.app.sanitize_otel_errors = True

        with session_context(mock_session):
            assert should_sanitize_errors(mock_session) is True

    def test_should_not_sanitize_with_flag_disabled(self, mock_session):
        """Test that sanitization is disabled when app setting is False"""
        mock_session.app.sanitize_otel_errors = False

        with session_context(mock_session):
            assert should_sanitize_errors(mock_session) is False

    def test_should_sanitize_without_session(self):
        """Test that sanitization defaults to True when no session is available"""
        # Call without session context - should default to True for security
        assert should_sanitize_errors(None) is True

    def test_maybe_sanitize_regular_exception(self, mock_session):
        """Test that regular exceptions are sanitized when enabled"""
        mock_session.app.sanitize_otel_errors = True
        exc = ValueError("Database password is 'secret123'")

        with session_context(mock_session):
            sanitized = maybe_sanitize_error(exc, mock_session)

        assert isinstance(sanitized, ValueError)
        assert str(sanitized) == mock_session.app.sanitize_error_msg
        assert "secret123" not in str(sanitized)

    def test_maybe_sanitize_safe_exception_bypasses(self, mock_session):
        """Test that SafeException bypasses sanitization"""
        mock_session.app.sanitize_otel_errors = True
        exc = SafeException("This is safe to show")

        with session_context(mock_session):
            result = maybe_sanitize_error(exc, mock_session)

        # Should return the original exception
        assert result is exc
        assert str(result) == "This is safe to show"

    def test_maybe_sanitize_disabled_returns_original(self, mock_session):
        """Test that exceptions are not sanitized when disabled"""
        mock_session.app.sanitize_otel_errors = False
        exc = ValueError("Sensitive information")

        with session_context(mock_session):
            result = maybe_sanitize_error(exc, mock_session)

        # Should return the original exception
        assert result is exc
        assert str(result) == "Sensitive information"

    def test_maybe_sanitize_without_session_sanitizes_by_default(self):
        """Test that exceptions are sanitized by default without session context"""
        from shiny._app import SANITIZE_ERROR_MSG

        exc = ValueError("Some error")
        result = maybe_sanitize_error(exc, None)

        # Should return sanitized exception (defaults to True for security)
        assert result is not exc
        assert str(result) == SANITIZE_ERROR_MSG
        assert "Some error" not in str(result)

    def test_maybe_sanitize_preserves_exception_type(self, mock_session):
        """Test that sanitization preserves exception type"""
        mock_session.app.sanitize_otel_errors = True
        exc = RuntimeError("Original message")

        with session_context(mock_session):
            sanitized = maybe_sanitize_error(exc, mock_session)

        # Should preserve the exception type
        assert isinstance(sanitized, RuntimeError)


class TestSpanExceptionRecording:
    """Tests for exception recording in spans"""

    def test_regular_exception_recorded_in_span(self, otel_tracer_provider):
        """Test that regular exceptions are recorded in spans"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):
            from shiny.otel import OtelCollectLevel
            from shiny.otel._span_wrappers import with_otel_span_async

            async def test_func():
                async with with_otel_span_async(
                    "test_span", level=OtelCollectLevel.SESSION
                ):
                    raise ValueError("Test error")

            # Run the async function and catch the exception
            import asyncio

            with pytest.raises(ValueError, match="Test error"):
                asyncio.run(test_func())

        # Check spans
        spans = get_exported_spans(provider, exporter)
        app_spans = [s for s in spans if s.name == "test_span"]
        assert len(app_spans) == 1

        span = app_spans[0]
        # Should have error status
        assert span.status.status_code == StatusCode.ERROR
        # Should have recorded exception
        assert len(span.events) > 0
        exception_events = [e for e in span.events if e.name == "exception"]
        assert len(exception_events) == 1
        assert "ValueError" in str(exception_events[0].attributes)

    def test_silent_exception_not_recorded_in_span(self, otel_tracer_provider):
        """Test that silent exceptions are not recorded in spans"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):
            from shiny.otel import OtelCollectLevel
            from shiny.otel._span_wrappers import with_otel_span_async

            async def test_func():
                async with with_otel_span_async(
                    "test_span", level=OtelCollectLevel.SESSION
                ):
                    raise SilentException("Silent error")

            # Run the async function and catch the exception
            import asyncio

            with pytest.raises(SilentException):
                asyncio.run(test_func())

        # Check spans
        spans = get_exported_spans(provider, exporter)
        app_spans = [s for s in spans if s.name == "test_span"]
        assert len(app_spans) == 1

        span = app_spans[0]
        # Should NOT have error status (silent exceptions don't count as errors)
        assert span.status.status_code != StatusCode.ERROR
        # Should NOT have recorded exception
        exception_events = [e for e in span.events if e.name == "exception"]
        assert len(exception_events) == 0

    def test_sanitized_exception_message_in_span(
        self, otel_tracer_provider, mock_session
    ):
        """Test that exception messages are sanitized in spans when enabled"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        # Enable sanitization for OTel
        mock_session.app.sanitize_otel_errors = True

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                from shiny.otel import OtelCollectLevel
                from shiny.otel._span_wrappers import with_otel_span_async

                async def test_func():
                    async with with_otel_span_async(
                        "test_span", level=OtelCollectLevel.SESSION
                    ):
                        raise ValueError("Database password is 'secret123'")

                # Run the async function and catch the exception
                import asyncio

                with pytest.raises(ValueError):
                    asyncio.run(test_func())

        # Check spans
        spans = get_exported_spans(provider, exporter)
        app_spans = [s for s in spans if s.name == "test_span"]
        assert len(app_spans) == 1

        span = app_spans[0]
        # Should have error status
        assert span.status.status_code == StatusCode.ERROR
        # Should have recorded exception with sanitized message
        exception_events = [e for e in span.events if e.name == "exception"]
        assert len(exception_events) == 1
        # Check that the message is sanitized
        assert "secret123" not in str(exception_events[0].attributes)
        assert mock_session.app.sanitize_error_msg in str(span.status.description)

    def test_safe_exception_not_sanitized_in_span(
        self, otel_tracer_provider, mock_session
    ):
        """Test that SafeException messages are not sanitized even when enabled"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        # Enable sanitization for OTel
        mock_session.app.sanitize_otel_errors = True

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                from shiny.otel import OtelCollectLevel
                from shiny.otel._span_wrappers import with_otel_span_async

                async def test_func():
                    async with with_otel_span_async(
                        "test_span", level=OtelCollectLevel.SESSION
                    ):
                        raise SafeException("This is safe to show")

                # Run the async function and catch the exception
                import asyncio

                with pytest.raises(SafeException):
                    asyncio.run(test_func())

        # Check spans
        spans = get_exported_spans(provider, exporter)
        app_spans = [s for s in spans if s.name == "test_span"]
        assert len(app_spans) == 1

        span = app_spans[0]
        # Should have error status
        assert span.status.status_code == StatusCode.ERROR
        # Should have recorded exception with original message
        exception_events = [e for e in span.events if e.name == "exception"]
        assert len(exception_events) == 1
        # Check that the original message is preserved
        assert "This is safe to show" in str(span.status.description)

    def test_sync_span_exception_handling(self, otel_tracer_provider):
        """Test that sync span wrapper also handles exceptions correctly"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):
            from shiny.otel import OtelCollectLevel
            from shiny.otel._span_wrappers import with_otel_span

            with pytest.raises(ValueError, match="Sync error"):
                with with_otel_span("sync_span", level=OtelCollectLevel.SESSION):
                    raise ValueError("Sync error")

        # Check spans
        spans = get_exported_spans(provider, exporter)
        app_spans = [s for s in spans if s.name == "sync_span"]
        assert len(app_spans) == 1

        span = app_spans[0]
        # Should have error status
        assert span.status.status_code == StatusCode.ERROR
        # Should have recorded exception
        exception_events = [e for e in span.events if e.name == "exception"]
        assert len(exception_events) == 1

    def test_sync_span_silent_exception_not_recorded(self, otel_tracer_provider):
        """Test that sync span wrapper doesn't record silent exceptions"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):
            from shiny.otel import OtelCollectLevel
            from shiny.otel._span_wrappers import with_otel_span

            with pytest.raises(SilentException):
                with with_otel_span("sync_span", level=OtelCollectLevel.SESSION):
                    raise SilentException("Silent")

        # Check spans
        spans = get_exported_spans(provider, exporter)
        app_spans = [s for s in spans if s.name == "sync_span"]
        assert len(app_spans) == 1

        span = app_spans[0]
        # Should NOT have error status
        assert span.status.status_code != StatusCode.ERROR
        # Should NOT have recorded exception
        exception_events = [e for e in span.events if e.name == "exception"]
        assert len(exception_events) == 0

    def test_session_id_in_error_span(self, otel_tracer_provider, mock_session):
        """Test that session ID is included in error span attributes"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                from shiny.otel import OtelCollectLevel
                from shiny.otel._span_wrappers import with_otel_span_async

                async def test_func():
                    async with with_otel_span_async(
                        "test_span", level=OtelCollectLevel.SESSION
                    ):
                        raise ValueError("Test error")

                import asyncio

                with pytest.raises(ValueError):
                    asyncio.run(test_func())

        # Check spans
        spans = get_exported_spans(provider, exporter)
        app_spans = [s for s in spans if s.name == "test_span"]
        assert len(app_spans) == 1

        span = app_spans[0]
        # Should have session.id attribute
        assert span.attributes is not None
        assert "session.id" in span.attributes
        assert span.attributes["session.id"] == "test-session-123"
