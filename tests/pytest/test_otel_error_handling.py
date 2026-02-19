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

import asyncio
from unittest.mock import Mock

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode

from shiny import App
from shiny._app import SANITIZE_ERROR_MSG
from shiny._namespaces import ResolvedId
from shiny.otel import OtelCollectLevel
from shiny.otel._errors import (
    has_otel_exception_been_recorded,
    is_silent_error,
    mark_otel_exception_as_recorded,
    maybe_sanitize_error,
    should_sanitize_errors,
)
from shiny.otel._span_wrappers import shiny_otel_span, shiny_otel_span_async
from shiny.session import Session, session_context
from shiny.types import (
    SafeException,
    SilentCancelOutputException,
    SilentException,
    SilentOperationInProgressException,
)

from .otel_helpers import get_exported_spans, patch_otel_tracing_state


@pytest.fixture
def mock_session():
    """Create a mock session for testing."""
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

    def test_should_sanitize_with_flag_enabled(self, mock_session: Session):
        """Test that sanitization is enabled when app setting is True"""
        mock_session.app.sanitize_otel_errors = True

        with session_context(mock_session):
            assert should_sanitize_errors(mock_session) is True

    def test_should_not_sanitize_with_flag_disabled(self, mock_session: Session):
        """Test that sanitization is disabled when app setting is False"""
        mock_session.app.sanitize_otel_errors = False

        with session_context(mock_session):
            assert should_sanitize_errors(mock_session) is False

    def test_should_sanitize_without_session(self):
        """Test that sanitization defaults to True when no session is available"""
        # Call without session context - should default to True for security
        assert should_sanitize_errors(None) is True

    def test_maybe_sanitize_regular_exception(self, mock_session: Session):
        """Test that regular exceptions are sanitized when enabled"""
        mock_session.app.sanitize_otel_errors = True
        exc = ValueError("Database password is 'secret123'")

        with session_context(mock_session):
            sanitized = maybe_sanitize_error(exc, mock_session)

        # Should return generic Exception type to avoid leaking info through exception type
        assert isinstance(sanitized, Exception)
        assert type(sanitized) is Exception  # Exactly Exception, not a subclass
        assert str(sanitized) == mock_session.app.sanitize_error_msg
        assert "secret123" not in str(sanitized)

    def test_maybe_sanitize_safe_exception_bypasses(self, mock_session: Session):
        """Test that SafeException bypasses sanitization"""
        mock_session.app.sanitize_otel_errors = True
        exc = SafeException("This is safe to show")

        with session_context(mock_session):
            result = maybe_sanitize_error(exc, mock_session)

        # Should return the original exception
        assert result is exc
        assert str(result) == "This is safe to show"

    def test_maybe_sanitize_disabled_returns_original(self, mock_session: Session):
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
        exc = ValueError("Some error")
        result = maybe_sanitize_error(exc, None)

        # Should return sanitized exception (defaults to True for security)
        assert result is not exc
        assert str(result) == SANITIZE_ERROR_MSG
        assert "Some error" not in str(result)

    def test_maybe_sanitize_uses_generic_exception_type(self, mock_session: Session):
        """Test that sanitization uses generic Exception type for security"""
        mock_session.app.sanitize_otel_errors = True
        exc = RuntimeError("Original message")

        with session_context(mock_session):
            sanitized = maybe_sanitize_error(exc, mock_session)

        # Should use generic Exception type to avoid leaking info through exception type
        assert isinstance(sanitized, Exception)
        assert type(sanitized) is Exception  # Exactly Exception, not a subclass


class TestSpanExceptionRecording:
    """Tests for exception recording in spans"""

    def test_regular_exception_recorded_in_span(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that regular exceptions are recorded in spans"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):
            from shiny.otel import OtelCollectLevel
            from shiny.otel._span_wrappers import shiny_otel_span_async

            async def test_func():
                async with shiny_otel_span_async(
                    "test_span", required_level=OtelCollectLevel.SESSION
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
        # When sanitized, should record as generic Exception type
        assert "Exception" in str(exception_events[0].attributes)

    def test_silent_exception_not_recorded_in_span(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that silent exceptions are not recorded in spans"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):
            from shiny.otel import OtelCollectLevel
            from shiny.otel._span_wrappers import shiny_otel_span_async

            async def test_func():
                async with shiny_otel_span_async(
                    "test_span", required_level=OtelCollectLevel.SESSION
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
        self,
        otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
        mock_session: Session,
    ):
        """Test that exception messages are sanitized in spans when enabled"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        # Enable sanitization for OTel
        mock_session.app.sanitize_otel_errors = True

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                from shiny.otel import OtelCollectLevel
                from shiny.otel._span_wrappers import shiny_otel_span_async

                async def test_func():
                    async with shiny_otel_span_async(
                        "test_span", required_level=OtelCollectLevel.SESSION
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
        self,
        otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
        mock_session: Session,
    ):
        """Test that SafeException messages are not sanitized even when enabled"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        # Enable sanitization for OTel
        mock_session.app.sanitize_otel_errors = True

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                from shiny.otel import OtelCollectLevel
                from shiny.otel._span_wrappers import shiny_otel_span_async

                async def test_func():
                    async with shiny_otel_span_async(
                        "test_span", required_level=OtelCollectLevel.SESSION
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

    def test_sync_span_exception_handling(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that sync span wrapper also handles exceptions correctly"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):
            from shiny.otel import OtelCollectLevel
            from shiny.otel._span_wrappers import shiny_otel_span

            with pytest.raises(ValueError, match="Sync error"):
                with shiny_otel_span(
                    "sync_span", required_level=OtelCollectLevel.SESSION
                ):
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

    def test_sync_span_silent_exception_not_recorded(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that sync span wrapper doesn't record silent exceptions"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):
            from shiny.otel import OtelCollectLevel
            from shiny.otel._span_wrappers import shiny_otel_span

            with pytest.raises(SilentException):
                with shiny_otel_span(
                    "sync_span", required_level=OtelCollectLevel.SESSION
                ):
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

    def test_session_id_in_error_span(
        self,
        otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
        mock_session: Session,
    ):
        """Test that session ID is included in error span attributes"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                from shiny.otel import OtelCollectLevel
                from shiny.otel._span_wrappers import shiny_otel_span_async

                async def test_func():
                    async with shiny_otel_span_async(
                        "test_span", required_level=OtelCollectLevel.SESSION
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


class TestExceptionRecordingOnce:
    """Tests for recording exceptions only once at innermost span"""

    def test_exception_marking_functions(self):
        """Test that exception marking functions work correctly"""
        exc = ValueError("Test error")

        # Initially, exception is not marked as recorded
        assert has_otel_exception_been_recorded(exc) is False

        # Mark it as recorded
        mark_otel_exception_as_recorded(exc)

        # Now it should be marked
        assert has_otel_exception_been_recorded(exc) is True

    def test_nested_spans_record_exception_once_async(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that nested async spans only record exception once at innermost span"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):

            async def test_func():
                # Parent span
                async with shiny_otel_span_async(
                    "parent_span", required_level=OtelCollectLevel.SESSION
                ):
                    # Child span where error originates
                    async with shiny_otel_span_async(
                        "child_span", required_level=OtelCollectLevel.SESSION
                    ):
                        raise ValueError("Test error from child")

            with pytest.raises(ValueError, match="Test error from child"):
                asyncio.run(test_func())

        # Check spans
        spans = get_exported_spans(provider, exporter)
        assert len(spans) == 2

        # Find parent and child spans
        child_span = next(s for s in spans if s.name == "child_span")
        parent_span = next(s for s in spans if s.name == "parent_span")

        # Both spans should have ERROR status
        assert child_span.status.status_code == StatusCode.ERROR
        assert parent_span.status.status_code == StatusCode.ERROR

        # Child span should have recorded the exception
        child_exception_events = [e for e in child_span.events if e.name == "exception"]
        assert len(child_exception_events) == 1
        # When sanitized, should record as generic Exception type
        assert "Exception" in str(child_exception_events[0].attributes)

        # Parent span should NOT have recorded the exception (already recorded by child)
        parent_exception_events = [
            e for e in parent_span.events if e.name == "exception"
        ]
        assert len(parent_exception_events) == 0

    def test_nested_spans_record_exception_once_sync(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that nested sync spans only record exception once at innermost span"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):
            with pytest.raises(ValueError, match="Test error from child"):
                # Parent span
                with shiny_otel_span(
                    "parent_span", required_level=OtelCollectLevel.SESSION
                ):
                    # Child span where error originates
                    with shiny_otel_span(
                        "child_span", required_level=OtelCollectLevel.SESSION
                    ):
                        raise ValueError("Test error from child")

        # Check spans
        spans = get_exported_spans(provider, exporter)
        assert len(spans) == 2

        # Find parent and child spans
        child_span = next(s for s in spans if s.name == "child_span")
        parent_span = next(s for s in spans if s.name == "parent_span")

        # Both spans should have ERROR status
        assert child_span.status.status_code == StatusCode.ERROR
        assert parent_span.status.status_code == StatusCode.ERROR

        # Child span should have recorded the exception
        child_exception_events = [e for e in child_span.events if e.name == "exception"]
        assert len(child_exception_events) == 1
        # When sanitized, should record as generic Exception type
        assert "Exception" in str(child_exception_events[0].attributes)

        # Parent span should NOT have recorded the exception (already recorded by child)
        parent_exception_events = [
            e for e in parent_span.events if e.name == "exception"
        ]
        assert len(parent_exception_events) == 0

    def test_triple_nested_spans_record_exception_once(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that triple-nested spans only record exception once at innermost span"""
        provider, exporter = otel_tracer_provider
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):

            async def test_func():
                # Grandparent span
                async with shiny_otel_span_async(
                    "grandparent_span", required_level=OtelCollectLevel.SESSION
                ):
                    # Parent span
                    async with shiny_otel_span_async(
                        "parent_span", required_level=OtelCollectLevel.SESSION
                    ):
                        # Child span where error originates
                        async with shiny_otel_span_async(
                            "child_span", required_level=OtelCollectLevel.SESSION
                        ):
                            raise ValueError("Test error from child")

            with pytest.raises(ValueError, match="Test error from child"):
                asyncio.run(test_func())

        # Check spans
        spans = get_exported_spans(provider, exporter)
        assert len(spans) == 3

        # Find all spans
        child_span = next(s for s in spans if s.name == "child_span")
        parent_span = next(s for s in spans if s.name == "parent_span")
        grandparent_span = next(s for s in spans if s.name == "grandparent_span")

        # All spans should have ERROR status
        assert child_span.status.status_code == StatusCode.ERROR
        assert parent_span.status.status_code == StatusCode.ERROR
        assert grandparent_span.status.status_code == StatusCode.ERROR

        # Only child span should have recorded the exception
        child_exception_events = [e for e in child_span.events if e.name == "exception"]
        assert len(child_exception_events) == 1

        # Parent and grandparent should NOT have recorded the exception
        parent_exception_events = [
            e for e in parent_span.events if e.name == "exception"
        ]
        assert len(parent_exception_events) == 0

        grandparent_exception_events = [
            e for e in grandparent_span.events if e.name == "exception"
        ]
        assert len(grandparent_exception_events) == 0
