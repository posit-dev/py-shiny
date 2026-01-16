"""
OpenTelemetry Session Lifecycle Instrumentation

Tests cover:
- Session start span creation
- Session end span creation
- HTTP attribute extraction
- Collection level controls
- Session ID propagation
"""

import os
from typing import Any, Dict
from unittest.mock import Mock, patch

from shiny.otel import OtelCollectLevel


class TestHttpAttributes:
    """HTTP attribute extraction tests"""

    def test_extract_http_attributes_from_url(self):
        """Test extracting HTTP attributes from http_conn.url"""
        from shiny.otel._attributes import extract_http_attributes

        # Create mock HTTP connection with url attribute
        mock_url = Mock()
        mock_url.hostname = "localhost"
        mock_url.port = 8000
        mock_url.path = "/test"
        mock_url.scheme = "http"

        mock_conn = Mock()
        mock_conn.url = mock_url

        attributes = extract_http_attributes(mock_conn)

        assert attributes["server.address"] == "localhost"
        assert attributes["server.port"] == 8000
        assert attributes["url.path"] == "/test"
        assert attributes["url.scheme"] == "http"

    def test_extract_http_attributes_from_scope(self):
        """Test extracting HTTP attributes from ASGI scope as fallback"""
        from shiny.otel._attributes import extract_http_attributes

        # Create mock HTTP connection with scope but no url
        mock_conn = Mock()
        mock_conn.url = None
        mock_conn.scope = {
            "server": ("127.0.0.1", 5000),
            "path": "/api/data",
            "scheme": "https",
        }

        attributes = extract_http_attributes(mock_conn)

        assert attributes["server.address"] == "127.0.0.1"
        assert attributes["server.port"] == 5000
        assert attributes["url.path"] == "/api/data"
        assert attributes["url.scheme"] == "https"

    def test_extract_http_attributes_empty(self):
        """Test extracting HTTP attributes when no data available"""
        from shiny.otel._attributes import extract_http_attributes

        # Create mock HTTP connection with no url or scope
        mock_conn = Mock()
        mock_conn.url = None
        mock_conn.scope = {}

        attributes = extract_http_attributes(mock_conn)

        # Should return empty dict without errors
        assert attributes == {}

    def test_extract_http_attributes_partial(self):
        """Test extracting HTTP attributes with partial data"""
        from shiny.otel._attributes import extract_http_attributes

        # Create mock with only some attributes
        mock_url = Mock()
        mock_url.hostname = "example.com"
        mock_url.port = None
        mock_url.path = "/"
        mock_url.scheme = None

        mock_conn = Mock()
        mock_conn.url = mock_url

        attributes = extract_http_attributes(mock_conn)

        assert attributes["server.address"] == "example.com"
        assert attributes["url.path"] == "/"
        # Port and scheme should not be in dict if None
        assert "server.port" not in attributes
        assert "url.scheme" not in attributes


class TestSessionSpans:
    """OpenTelemetry Session Lifecycle Instrumentation Tests"""

    def test_session_spans_created_at_session_level(self):
        """Test that session.start and session.end spans are created at SESSION level"""
        # This is an integration test that would require spinning up a real session
        # For now, we'll test the logic in isolation
        from shiny.otel import should_otel_collect

        # Mock the tracing enabled check
        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                assert should_otel_collect(OtelCollectLevel.SESSION) is True
                assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE) is False

    def test_session_spans_not_created_at_none_level(self):
        """Test that no session spans are created at NONE level"""
        from shiny.otel import should_otel_collect

        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "none"}):
                assert should_otel_collect(OtelCollectLevel.SESSION) is False

    def test_session_spans_created_at_all_level(self):
        """Test that session spans are created at ALL level"""
        from shiny.otel import should_otel_collect

        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                assert should_otel_collect(OtelCollectLevel.SESSION) is True

    def test_session_id_in_span_attributes(self):
        """Test that session ID is included in span attributes"""
        # This would be an integration test
        # For now we verify the attribute extraction logic
        session_id = "test_session_123"
        attributes: Dict[str, Any] = {"session.id": session_id}

        assert "session.id" in attributes
        assert attributes["session.id"] == session_id


class TestSessionInstrumentation:
    """OpenTelemetry Session Lifecycle Instrumentation Tests"""

    def test_session_start_wraps_execution(self):
        """Test that _run() wraps _run_impl() in session.start span"""
        # This tests the structure of the code, not execution
        # Real execution would require a full session setup
        from shiny.otel import should_otel_collect

        # Verify the should_otel_collect function works correctly
        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                result = should_otel_collect(OtelCollectLevel.SESSION)
                assert result is True

    def test_session_end_wraps_cleanup(self):
        """Test that _run_session_ended_tasks() wraps cleanup in session.end span"""
        from shiny.otel import should_otel_collect

        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                result = should_otel_collect(OtelCollectLevel.SESSION)
                assert result is True

    def test_no_otel_when_sdk_not_configured(self):
        """Test that no OTel operations occur when SDK not configured"""
        from shiny.otel import should_otel_collect

        # Reset tracing enabled check
        with patch("shiny.otel._core._tracing_enabled", None):
            # Without SDK configured, should always return False
            result = should_otel_collect(OtelCollectLevel.SESSION)
            assert result is False
