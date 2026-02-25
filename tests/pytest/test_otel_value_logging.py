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
def _otel_log_provider_session() -> (
    Iterator[Tuple[LoggerProvider, InMemoryLogRecordExporter]]
):
    """
    Internal session-scoped fixture for OpenTelemetry LoggerProvider.

    Creates a single LoggerProvider and InMemoryLogRecordExporter for the entire
    test session. This is wrapped by the otel_log_provider_and_exporter fixture
    which provides automatic log clearing before each test.

    Why session-scoped?
    -------------------
    OpenTelemetry uses a global singleton for the logger provider. Calling
    set_logger_provider() multiple times causes warnings ("Overriding of current
    LoggerProvider is not allowed") and potential state corruption. Session scope
    ensures the provider is set once per pytest worker process, avoiding conflicts
    during parallel test execution.
    """
    # Create in-memory exporter and logger provider
    memory_exporter = InMemoryLogRecordExporter()
    provider = LoggerProvider()
    provider.add_log_record_processor(SimpleLogRecordProcessor(memory_exporter))

    # Set as global logger provider (can only be done once per process)
    set_logger_provider(provider)

    # Reset OTel state to pick up new provider
    reset_otel_tracing_state()

    yield provider, memory_exporter

    # Cleanup - no need to restore, pytest handles it


@pytest.fixture
def otel_log_provider_and_exporter(
    _otel_log_provider_session: Tuple[LoggerProvider, InMemoryLogRecordExporter],
) -> Tuple[LoggerProvider, InMemoryLogRecordExporter]:
    """
    Function-scoped fixture for OpenTelemetry LoggerProvider.

    Provides access to a session-scoped LoggerProvider and InMemoryLogRecordExporter,
    automatically clearing logs before each test to ensure test isolation.

    Why two fixtures instead of one?
    --------------------------------
    We cannot merge this into one function-scoped fixture because:
    1. The provider must be set globally once per worker (session scope)
    2. The exporter must be cleared per test (function scope)
    3. Creating new providers per test would repeatedly call
       set_logger_provider(), causing warnings and state corruption

    This two-fixture pattern separates the one-time global setup (session)
    from the per-test cleanup (function), working correctly with pytest-xdist.

    Returns
    -------
    tuple[LoggerProvider, InMemoryLogRecordExporter]
        The provider and exporter for use in tests.
    """
    provider, exporter = _otel_log_provider_session
    # Clear logs from previous tests to ensure isolation
    exporter.clear()
    return provider, exporter


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
        emit_otel_log("Debug message", severity_text="DEBUG")

        provider.force_flush()
        logs = exporter.get_finished_logs()

        test_logs = [log for log in logs if log.log_record.body == "Debug message"]
        assert len(test_logs) == 1
        assert test_logs[0].log_record.severity_text == "DEBUG"

    def test_emit_log_with_attributes(self, otel_log_provider_and_exporter):
        """Test log emission with attributes"""
        provider, exporter = otel_log_provider_and_exporter
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
        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                # Simulate setting collection level to REACTIVITY
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    # Create a value and set its name
                    val = reactive.Value[int]()
                    val._name = "test_value"

                    # Set the value
                    val.set(42)

        # Check logs
        provider.force_flush()
        logs = exporter.get_finished_logs()

        # Find our log
        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        assert len(value_logs) >= 1

        # Check the log details
        log = value_logs[0]
        assert log.log_record.body == "Set reactive.value test_value"
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
        # Set up session with namespace
        mock_session.ns = ResolvedId("mymodule")

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    val = reactive.Value[int]()
                    val._name = "my_input"
                    val.set(100)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        assert len(value_logs) >= 1
        assert value_logs[0].log_record.body == "Set reactive.value mymodule:my_input"

    def test_value_set_unnamed(self, otel_log_provider_and_exporter, mock_session):
        """Test that unnamed values log as <anonymous>"""
        provider, exporter = otel_log_provider_and_exporter
        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    val = reactive.Value[int]()
                    val._name = ""
                    val.set(42)

                    val2 = reactive.Value[int]()
                    val2._name = None
                    val2.set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        assert len(value_logs) >= 2
        assert value_logs[0].log_record.body == "Set reactive.value <anonymous>"
        assert value_logs[1].log_record.body == "Set reactive.value <anonymous>"

    def test_name_unset_from_fn(self, otel_log_provider_and_exporter, mock_session):
        """Test that if name is unset from function, it logs as <anonymous>"""
        provider, exporter = otel_log_provider_and_exporter

        def make_value():
            return reactive.Value[int]()

        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    val = make_value()
                    val.set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        assert len(value_logs) >= 1
        assert value_logs[0].log_record.body == "Set reactive.value <anonymous>"

    def test_value_set_no_session(self, otel_log_provider_and_exporter):
        """Test that value updates do NOT log without a session (too early)"""
        provider, exporter = otel_log_provider_and_exporter
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                val = reactive.Value[int]()
                val._name = "standalone_value"
                val.set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        # Should have NO logs without a session (intentionally returns early)
        assert len(value_logs) == 0

    def test_value_set_no_log_when_tracing_disabled(
        self, otel_log_provider_and_exporter
    ):
        """Test that no logs are emitted when tracing is disabled"""
        provider, exporter = otel_log_provider_and_exporter
        with patch_otel_tracing_state(tracing_enabled=False):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                val = reactive.Value[int]()
                val._name = "test_value"
                val.set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        # Should not find any value update logs
        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        assert len(value_logs) == 0

    def test_value_set_no_log_when_collection_level_low(
        self, otel_log_provider_and_exporter, mock_session
    ):
        """Test that no logs are emitted when collection level is below REACTIVITY"""
        provider, exporter = otel_log_provider_and_exporter
        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                # Set collection level to SESSION (below REACTIVITY)
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                    val = reactive.Value[int]()
                    val._name = "test_value"
                    val.set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        # Should not find any value update logs
        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        assert len(value_logs) == 0

    def test_value_set_multiple_updates(
        self, otel_log_provider_and_exporter, mock_session
    ):
        """Test that multiple value updates each produce a log"""
        provider, exporter = otel_log_provider_and_exporter
        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    val = reactive.Value[int]()
                    val._name = "counter"

                    # Set multiple times
                    val.set(1)
                    val.set(2)
                    val.set(3)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body
            and "Set reactive.value counter" in log.log_record.body
        ]
        # Should have 3 logs for 3 updates
        assert len(value_logs) == 3

    def test_value_set_same_value_no_update(
        self, otel_log_provider_and_exporter, mock_session
    ):
        """Test that setting same value doesn't log (because _set returns False)"""
        provider, exporter = otel_log_provider_and_exporter
        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    val = reactive.Value[int](42)
                    val._name = "test_value"

                    # Clear any initial logs
                    # Set to same value - should return False and not log
                    result = val.set(42)
                    assert result is False

        provider.force_flush()
        logs = exporter.get_finished_logs()

        # Should not have any logs because value didn't change
        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        assert len(value_logs) == 0

    def test_read_only_attribute_in_logs(
        self, otel_log_provider_and_exporter, mock_session
    ):
        """Test that read-only values have read-only attribute in logs"""
        provider, exporter = otel_log_provider_and_exporter
        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    # Create read-only value
                    readonly_val = reactive.Value[int](42, read_only=True)
                    readonly_val._name = "readonly_val"
                    readonly_val._set(100)  # Use _set to bypass read-only check

                    # Create regular (non-read-only) value
                    regular_val = reactive.Value[int]()
                    regular_val._name = "regular_val"
                    regular_val.set(200)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        # Find read-only value log
        readonly_logs = [
            log
            for log in logs
            if log.log_record.body and "readonly_val" in log.log_record.body
        ]
        assert len(readonly_logs) >= 1
        readonly_log = readonly_logs[0]
        assert readonly_log.log_record.attributes is not None
        assert readonly_log.log_record.attributes.get("read-only") is True

        # Find regular value log - should have read-only=False
        regular_logs = [
            log
            for log in logs
            if log.log_record.body and "regular_val" in log.log_record.body
        ]
        assert len(regular_logs) >= 1
        regular_log = regular_logs[0]
        assert regular_log.log_record.attributes is not None
        # read-only attribute should not exist for non-read-only values
        assert "read-only" not in regular_log.log_record.attributes


class TestValueNaming:
    """Tests for reactive Value naming (explicit and automatic inference)"""

    def test_explicit_name_parameter(self):
        """Test that explicit name parameter is used"""
        val = reactive.Value(0, name="my_counter")
        assert val._name == "my_counter"

    def test_inferred_name_simple_assignment(self):
        """Test that simple assignment names are inferred"""
        test_value = reactive.Value(0)
        assert test_value._name == "test_value"

    def test_inferred_name_simple_assignment_lowercase(self):
        """Test that simple assignment names are inferred with lowercase value()"""
        test_value_lower = reactive.value(0)
        assert test_value_lower._name == "test_value_lower"

    def test_inferred_name_attribute_assignment(self):
        """Test that attribute assignment names are inferred"""

        class Container:
            def __init__(self):
                self.counter = reactive.Value(0)

        obj = Container()
        assert obj.counter._name == "counter"

    def test_inferred_name_attribute_assignment_lowercase(self):
        """Test that attribute assignment names are inferred with lowercase value()"""

        class Container:
            def __init__(self):
                self.counter_lower = reactive.value(0)

        obj = Container()
        assert obj.counter_lower._name == "counter_lower"

    def test_inferred_name_simple_assignment_no_prefix(self):
        """Test that simple assignment names are inferred with Value (no prefix)"""
        from shiny.reactive import Value

        test_value_no_prefix = Value(0)
        assert test_value_no_prefix._name == "test_value_no_prefix"

    def test_inferred_name_simple_assignment_lowercase_no_prefix(self):
        """Test that simple assignment names are inferred with value (no prefix)"""
        from shiny.reactive import value

        test_value_lower_no_prefix = value(0)
        assert test_value_lower_no_prefix._name == "test_value_lower_no_prefix"

    def test_inferred_name_attribute_assignment_no_prefix(self):
        """Test that attribute assignment names are inferred with Value (no prefix)"""
        from shiny.reactive import Value

        class Container:
            def __init__(self):
                self.counter_no_prefix = Value(0)

        obj = Container()
        assert obj.counter_no_prefix._name == "counter_no_prefix"

    def test_inferred_name_attribute_assignment_lowercase_no_prefix(self):
        """Test that attribute assignment names are inferred with value (no prefix)"""
        from shiny.reactive import value

        class Container:
            def __init__(self):
                self.counter_lower_no_prefix = value(0)

        obj = Container()
        assert obj.counter_lower_no_prefix._name == "counter_lower_no_prefix"

    def test_explicit_name_overrides_inference(self):
        """Test that explicit name takes priority over inference"""
        explicit_name = reactive.Value(0, name="custom_name")
        assert explicit_name._name == "custom_name"

    def test_unnamed_value_when_inference_fails(self):
        """Test that name is None when inference fails"""
        # Create value in a way that inference can't detect (list comprehension)
        values = [reactive.Value(i) for i in range(3)]
        # Names should be None because inference fails for list comprehensions
        assert all(v._name is None for v in values)

    def test_name_used_in_logging(self, otel_log_provider_and_exporter, mock_session):
        """Test that explicit name is used in logs"""
        provider, exporter = otel_log_provider_and_exporter
        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    val = reactive.Value(0, name="explicit_counter")
                    val.set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        assert len(value_logs) >= 1
        assert value_logs[0].log_record.body == "Set reactive.value explicit_counter"

    def test_inferred_name_used_in_logging(
        self, otel_log_provider_and_exporter, mock_session
    ):
        """Test that inferred name is used in logs"""
        provider, exporter = otel_log_provider_and_exporter
        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    inferred_counter = reactive.Value(0)
                    inferred_counter.set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        assert len(value_logs) >= 1
        assert value_logs[0].log_record.body == "Set reactive.value inferred_counter"

    def test_inferred_name_used_in_logging_lowercase(
        self, otel_log_provider_and_exporter, mock_session
    ):
        """Test that inferred name is used in logs with lowercase value()"""
        provider, exporter = otel_log_provider_and_exporter
        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    inferred_counter_lower = reactive.value(0)
                    inferred_counter_lower.set(42)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        assert len(value_logs) >= 1
        assert (
            value_logs[0].log_record.body == "Set reactive.value inferred_counter_lower"
        )

    def test_name_can_be_overridden_after_creation(self):
        """Test that Inputs can override inferred names"""
        # Simulate what Inputs does
        my_input = reactive.Value(0)
        original_name = my_input._name

        # Inputs overrides the name
        my_input._name = "input.id"

        assert my_input._name == "input.id"
        assert my_input._name != original_name

    def test_inputs_sets_name_with_prefix(self, mock_session):
        """Test that Inputs class sets names with 'input.' prefix"""
        from shiny._namespaces import ResolvedId
        from shiny.session._session import Inputs

        # Create an Inputs object
        inputs = Inputs({}, ns=lambda x: ResolvedId(x))

        # Create a value and add it via __setitem__
        val = reactive.Value(42)
        inputs["my_slider"] = val

        # Should have input. prefix
        assert val._name == "input.my_slider"

    def test_inputs_getitem_sets_name_with_prefix(self):
        """Test that Inputs.__getitem__ auto-creates values with 'input.' prefix"""
        from shiny._namespaces import ResolvedId
        from shiny.session._session import Inputs

        # Create an Inputs object
        inputs = Inputs({}, ns=lambda x: ResolvedId(x))

        # Access a non-existent input (triggers auto-creation)
        val = inputs["slider"]

        # Should have input. prefix
        assert val._name == "input.slider"

    def test_inputs_skips_clientdata_prefix(self):
        """Test that Inputs skips 'input.' prefix for .clientdata_ keys via __setitem__"""
        from shiny._namespaces import ResolvedId
        from shiny.session._session import Inputs

        # Create an Inputs object
        inputs = Inputs({}, ns=lambda x: ResolvedId(x))

        # Create a value with explicit name to avoid inference
        val = reactive.Value(True, name="original_name")
        inputs[".clientdata_output_plot_hidden"] = val

        # Should use the full key as the name (not add input. prefix for keys starting with .)
        assert val._name == ".clientdata_output_plot_hidden"

    def test_inputs_getitem_skips_clientdata_prefix(self):
        """Test that Inputs.__getitem__ doesn't add 'input.' prefix for .clientdata_ keys"""
        from shiny._namespaces import ResolvedId
        from shiny.session._session import Inputs

        # Create an Inputs object
        inputs = Inputs({}, ns=lambda x: ResolvedId(x))

        # Access a .clientdata key (triggers auto-creation)
        val = inputs[".clientdata_output_plot_hidden"]

        # Should NOT have input. prefix (key starts with .)
        # The name should just be the original key
        assert val._name == ".clientdata_output_plot_hidden"


class TestValueSourceReference:
    """Tests for source reference tracking in value updates"""

    def test_source_ref_in_log_attributes(
        self, otel_log_provider_and_exporter, mock_session
    ):
        """Test that source reference attributes are included in logs"""
        provider, exporter = otel_log_provider_and_exporter
        with session_context(mock_session):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                    val = reactive.Value(0, name="test_value")
                    val.set(42)  # This line should be captured in source ref

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        assert len(value_logs) >= 1

        # Check that source reference attributes are present
        attrs = value_logs[0].log_record.attributes
        assert attrs is not None
        assert "code.filepath" in attrs
        assert "code.lineno" in attrs
        assert "code.function" in attrs

        # Verify the filepath points to this test file
        assert "test_otel_value_logging.py" in attrs["code.filepath"]
        # Verify the function is this test
        assert attrs["code.function"] == "test_source_ref_in_log_attributes"

    def test_source_ref_without_session(self, otel_log_provider_and_exporter):
        """Test that NO logs are emitted without a session (too early)"""
        provider, exporter = otel_log_provider_and_exporter
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                val = reactive.Value(0, name="standalone")
                val.set(100)

        provider.force_flush()
        logs = exporter.get_finished_logs()

        value_logs = [
            log
            for log in logs
            if log.log_record.body and "Set reactive.value" in log.log_record.body
        ]
        # Should have NO logs without a session (intentionally returns early)
        assert len(value_logs) == 0
