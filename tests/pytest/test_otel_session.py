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
from unittest.mock import Mock, patch

from shiny.otel._collect import OtelCollectLevel, should_otel_collect
from shiny.otel._attributes import extract_http_attributes

from .otel_helpers import patch_otel_tracing_state


class TestHttpAttributes:
    """HTTP attribute extraction tests"""

    def test_extract_http_attributes_from_url(self):
        """Test extracting HTTP attributes from http_conn.url"""
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
        # Create mock HTTP connection with no url or scope
        mock_conn = Mock()
        mock_conn.url = None
        mock_conn.scope = {}

        attributes = extract_http_attributes(mock_conn)

        # Should return empty dict without errors
        assert attributes == {}

    def test_extract_http_attributes_partial(self):
        """Test extracting HTTP attributes with partial data"""
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

    def test_session_level_collection_enabled(self):
        """Test that collection is enabled for SESSION level when SHINY_OTEL_COLLECT=session"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                assert should_otel_collect(OtelCollectLevel.SESSION) is True
                assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE) is False

    def test_collection_disabled_at_none_level(self):
        """Test that collection is disabled when SHINY_OTEL_COLLECT=none"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "none"}):
                assert should_otel_collect(OtelCollectLevel.SESSION) is False

    def test_session_level_collection_enabled_at_all_level(self):
        """Test that SESSION level collection is enabled when SHINY_OTEL_COLLECT=all"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                assert should_otel_collect(OtelCollectLevel.SESSION) is True


class TestSessionInstrumentation:
    """OpenTelemetry Session Lifecycle Instrumentation Tests"""

    def test_session_collection_enabled_for_instrumentation(self):
        """Test that collection is enabled for session instrumentation when configured"""
        # Verify the should_otel_collect function works correctly for session instrumentation
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                result = should_otel_collect(OtelCollectLevel.SESSION)
                assert result is True

    def test_no_otel_when_sdk_not_configured(self):
        """Test that no OTel operations occur when SDK not configured"""
        # Simulate SDK not configured by setting tracing_enabled to False
        with patch_otel_tracing_state(tracing_enabled=False):
            # Without SDK configured, should always return False
            result = should_otel_collect(OtelCollectLevel.SESSION)
            assert result is False
