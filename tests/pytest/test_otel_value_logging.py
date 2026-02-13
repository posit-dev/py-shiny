"""
OpenTelemetry Value Update Logging

Tests cover:
- Log emission when reactive values are updated
- Log message format and content
- Session ID attribute inclusion
- Collection level controls
- Namespace support in log messages
- No-op behavior when OTel SDK not configured

Note: Type checking is partially suppressed for OpenTelemetry SDK internal types
which don't have complete type stubs available.
"""

# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportMissingParameterType=false

import os
from typing import Iterator, Tuple
from unittest.mock import Mock, patch

import pytest
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import (
    InMemoryLogRecordExporter,
    SimpleLogRecordProcessor,
)

from shiny import reactive
from shiny._namespaces import ResolvedId
from shiny.otel._core import emit_otel_log
from shiny.session import Session, session_context

from .otel_helpers import patch_otel_tracing_state, reset_otel_tracing_state


@pytest.fixture(scope="session")
def otel_log_provider_and_exporter() -> (
    Iterator[Tuple[LoggerProvider, InMemoryLogRecordExporter]]
):
    """
    Set up an OpenTelemetry LoggerProvider with in-memory exporter for testing.

    This fixture creates a session-scoped LoggerProvider that collects logs
    in memory, allowing tests to verify log emission without external dependencies.

    Returns
    -------
    tuple[LoggerProvider, InMemoryLogRecordExporter]
        The provider and exporter for use in tests.
    """
    # Create in-memory exporter and logger provider
    memory_exporter = InMemoryLogRecordExporter()
    provider = LoggerProvider()
    provider.add_log_record_processor(SimpleLogRecordProcessor(memory_exporter))

    # Set as global logger provider
    set_logger_provider(provider)

    # Reset OTel state to pick up new provider
    reset_otel_tracing_state()

    yield provider, memory_exporter

    # Cleanup - no need to restore, pytest handles it


@pytest.fixture
def mock_session() -> Mock:
    """Create a mock session for testing."""
    session = Mock(spec=Session)
    session.id = "test-session-123"
    session.ns = ResolvedId("")  # Root namespace
    return session


class TestEmitLog:
    """Tests for the emit_otel_log helper function"""

    def test_emit_log_basic(self, otel_log_provider_and_exporter):
        """Test basic log emission"""
        provider, exporter = otel_log_provider_and_exporter
        exporter.clear()

        emit_otel_log("Test message")

        # Force flush and get logs
        provider.force_flush()
        logs = exporter.get_finished_logs()

        assert len(logs) >= 1
        # Find our log message
        test_logs = [log for log in logs if log.log_record.body == "Test message"]
        assert len(test_logs) == 1
        assert test_logs[0].log_record.severity_text == "INFO"

    def test_emit_log_with_severity(self, otel_log_provider_and_exporter):
        """Test log emission with custom severity"""
        provider, exporter = otel_log_provider_and_exporter
        exporter.clear()

        emit_otel_log("Debug message", severity_text="DEBUG")

        provider.force_flush()
        logs = exporter.get_finished_logs()

        test_logs = [log for log in logs if log.log_record.body == "Debug message"]
        assert len(test_logs) == 1
        assert test_logs[0].log_record.severity_text == "DEBUG"

    def test_emit_log_with_attributes(self, otel_log_provider_and_exporter):
        """Test log emission with attributes"""
        provider, exporter = otel_log_provider_and_exporter
        exporter.clear()

        emit_otel_log(
            "Test with attributes",
            attributes={"session.id": "test-123", "custom.key": "value"},
        )

        provider.force_flush()
        logs = exporter.get_finished_logs()

        test_logs = [
            log for log in logs if log.log_record.body == "Test with attributes"
        ]
        assert len(test_logs) == 1
        attrs = test_logs[0].log_record.attributes
        assert attrs is not None
        assert attrs.get("session.id") == "test-123"
        assert attrs.get("custom.key") == "value"

    def test_emit_log_no_provider(self):
        """Test that emit_log doesn't raise when no provider is configured"""
        # Reset to no provider
        reset_otel_tracing_state()

        # Should not raise
        emit_otel_log("Test message")


class TestValueUpdateLogging:
    """Tests for reactive Value update logging"""

    def test_value_set_logs_update(self, otel_log_provider_and_exporter, mock_session):
        """Test that setting a value logs an update"""
        provider, exporter = otel_log_provider_and_exporter
        exporter.clear()

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                # Simulate setting collection level to REACTIVITY
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    # Create a value and set its name
                    val = reactive.Value[int]()
                    val._name = "test_value"

                    # Set the value
                    val._set(42)

        # Check logs
        provider.force_flush()
        logs = exporter.get_finished_logs()

        # Find our log
        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactiveVal" in log.log_record.body
        ]
        assert len(value_logs) >= 1

        # Check the log details
        log = value_logs[0]
        assert log.log_record.body == "Set reactiveVal test_value"
        assert log.log_record.severity_text == "DEBUG"

        # Check session ID attribute
        attrs = log.log_record.attributes
        assert attrs is not None
        assert attrs.get("session.id") == "test-session-123"

    def test_value_set_with_namespace(
        self, otel_log_provider_and_exporter, mock_session
    ):
        """Test that value updates include namespace in log message"""
        provider, exporter = otel_log_provider_and_exporter
        exporter.clear()

        # Set up session with namespace
        mock_session.ns = ResolvedId("mymodule")

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    val = reactive.Value[int]()
                    val._name = "my_input"
                    val._set(100)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactiveVal" in log.log_record.body
        ]
        assert len(value_logs) >= 1
        assert value_logs[0].log_record.body == "Set reactiveVal mymodule:my_input"

    def test_value_set_unnamed(self, otel_log_provider_and_exporter, mock_session):
        """Test that unnamed values log as <unnamed>"""
        provider, exporter = otel_log_provider_and_exporter
        exporter.clear()

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    val = reactive.Value[int]()
                    # Don't set name
                    val._set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactiveVal" in log.log_record.body
        ]
        assert len(value_logs) >= 1
        assert value_logs[0].log_record.body == "Set reactiveVal <unnamed>"

    def test_value_set_no_session(self, otel_log_provider_and_exporter):
        """Test that value updates work without a session"""
        provider, exporter = otel_log_provider_and_exporter
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                val = reactive.Value[int]()
                val._name = "standalone_value"
                val._set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactiveVal" in log.log_record.body
        ]
        assert len(value_logs) >= 1
        assert value_logs[0].log_record.body == "Set reactiveVal standalone_value"

        # Session ID should not be present
        attrs = value_logs[0].log_record.attributes
        # attrs could be None or not contain session.id
        if attrs is not None:
            assert "session.id" not in attrs

    def test_value_set_no_log_when_tracing_disabled(
        self, otel_log_provider_and_exporter
    ):
        """Test that no logs are emitted when tracing is disabled"""
        provider, exporter = otel_log_provider_and_exporter
        exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=False):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                val = reactive.Value[int]()
                val._name = "test_value"
                val._set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        # Should not find any value update logs
        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactiveVal" in log.log_record.body
        ]
        assert len(value_logs) == 0

    def test_value_set_no_log_when_collection_level_low(
        self, otel_log_provider_and_exporter, mock_session
    ):
        """Test that no logs are emitted when collection level is below REACTIVITY"""
        provider, exporter = otel_log_provider_and_exporter
        exporter.clear()

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                # Set collection level to SESSION (below REACTIVITY)
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                    val = reactive.Value[int]()
                    val._name = "test_value"
                    val._set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        # Should not find any value update logs
        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactiveVal" in log.log_record.body
        ]
        assert len(value_logs) == 0

    def test_value_set_multiple_updates(
        self, otel_log_provider_and_exporter, mock_session
    ):
        """Test that multiple value updates each produce a log"""
        provider, exporter = otel_log_provider_and_exporter
        exporter.clear()

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    val = reactive.Value[int]()
                    val._name = "counter"

                    # Set multiple times
                    val._set(1)
                    val._set(2)
                    val._set(3)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactiveVal counter" in log.log_record.body
        ]
        # Should have 3 logs for 3 updates
        assert len(value_logs) == 3

    def test_value_set_same_value_no_update(
        self, otel_log_provider_and_exporter, mock_session
    ):
        """Test that setting same value doesn't log (because _set returns False)"""
        provider, exporter = otel_log_provider_and_exporter
        exporter.clear()

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    val = reactive.Value[int](42)
                    val._name = "test_value"

                    # Clear any initial logs
                    exporter.clear()

                    # Set to same value - should return False and not log
                    result = val._set(42)
                    assert result is False

        provider.force_flush()
        logs = exporter.get_finished_logs()

        # Should not have any logs because value didn't change
        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactiveVal" in log.log_record.body
        ]
        assert len(value_logs) == 0
