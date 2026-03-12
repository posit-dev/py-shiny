"""
OpenTelemetry Foundation (Core Infrastructure)

Tests cover:
- Lazy tracer/logger initialization
- Collection level management
- Environment variable configuration
- No-op behavior when SDK not configured
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shiny.otel._collect import OtelCollectLevel, get_level
from shiny.otel._core import (
    detached_otel_context,
    get_otel_logger,
    get_otel_tracer,
    is_otel_tracing_enabled,
)
from shiny.otel._span_wrappers import shiny_otel_span
from shiny.session._utils import session_context

from .otel_helpers import get_exported_spans, patch_otel_tracing_state


class TestCore:
    """Tests for shiny/otel/_core.py"""

    def test_get_otel_tracer_returns_tracer(self):
        """Test that get_otel_tracer() returns a tracer instance."""
        tracer = get_otel_tracer()
        assert tracer is not None
        # Should return same instance on subsequent calls
        assert get_otel_tracer() is tracer

    def test_get_otel_logger_returns_logger(self):
        """Test that get_otel_logger() returns a logger instance."""
        logger = get_otel_logger()
        assert logger is not None
        # Should return same instance on subsequent calls
        assert get_otel_logger() is logger

    def test_is_otel_tracing_enabled_without_sdk(self):
        """Test that is_otel_tracing_enabled() returns False when SDK not configured."""
        # Force tracing disabled to simulate no SDK configuration
        with patch_otel_tracing_state(tracing_enabled=False):
            # Without SDK, tracing should be disabled
            assert is_otel_tracing_enabled() is False

    def test_is_otel_tracing_enabled_creates_no_spans(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that is_otel_tracing_enabled() doesn't create spans when called."""
        from .otel_helpers import get_exported_spans

        provider, exporter = otel_tracer_provider

        # Enable tracing
        with patch_otel_tracing_state(tracing_enabled=True):
            # Call the function multiple times
            for _ in range(10):
                is_otel_tracing_enabled()

        # Verify no spans were created
        spans = get_exported_spans(provider, exporter)
        assert len(spans) == 0, "is_otel_tracing_enabled() should not create any spans"


class TestDetachedOtelContext:
    """Tests for detached_otel_context()"""

    def test_spans_inside_have_no_parent(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Spans created inside detached_otel_context() are root spans (no parent)."""
        provider, exporter = otel_tracer_provider
        tracer = provider.get_tracer("test")

        with patch_otel_tracing_state(tracing_enabled=True):
            with tracer.start_as_current_span("parent"):
                with detached_otel_context():
                    with tracer.start_as_current_span("child"):
                        pass

        spans = get_exported_spans(provider, exporter)
        child = next(s for s in spans if s.name == "child")
        assert child.parent is None

    def test_outer_context_restored_after(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """The outer span context is restored after exiting detached_otel_context()."""
        provider, _ = otel_tracer_provider
        tracer = provider.get_tracer("test")

        with patch_otel_tracing_state(tracing_enabled=True):
            with tracer.start_as_current_span("parent") as parent_span:
                with detached_otel_context():
                    pass
                assert trace.get_current_span() is parent_span

    def test_no_op_when_opentelemetry_not_installed(self):
        """detached_otel_context() yields normally when opentelemetry is not installed."""
        otel_modules = {k: v for k, v in sys.modules.items() if "opentelemetry" in k}
        blocked = {k: None for k in otel_modules}
        with patch.dict(sys.modules, blocked):
            ran = False
            with detached_otel_context():
                ran = True
            assert ran


class TestOtelCollectLevel:
    """OtelCollectLevel enum tests"""

    def test_otel_collect_level_values(self):
        """Test that OtelCollectLevel enum has correct values."""
        assert OtelCollectLevel.NONE == 0
        assert OtelCollectLevel.SESSION == 1
        assert OtelCollectLevel.REACTIVE_UPDATE == 2
        assert OtelCollectLevel.REACTIVITY == 3
        assert OtelCollectLevel.ALL == 4

    def test_otel_collect_level_ordering(self):
        """Test that OtelCollectLevel values are correctly ordered."""
        assert OtelCollectLevel.NONE < OtelCollectLevel.SESSION
        assert OtelCollectLevel.SESSION < OtelCollectLevel.REACTIVE_UPDATE
        assert OtelCollectLevel.REACTIVE_UPDATE < OtelCollectLevel.REACTIVITY
        assert OtelCollectLevel.REACTIVITY < OtelCollectLevel.ALL


class TestGetOtelCollectLevel:
    """get_level() function tests"""

    def test_default_level(self):
        """Test that default collection level is ALL when no env var set."""
        with patch.dict(os.environ, {}, clear=True):
            # Clear the env var if it exists
            os.environ.pop("SHINY_OTEL_COLLECT", None)
            level = get_level()
            assert level == OtelCollectLevel.ALL

    @pytest.mark.parametrize(
        "env_value,expected",
        [
            ("none", OtelCollectLevel.NONE),
            ("NONE", OtelCollectLevel.NONE),
            ("session", OtelCollectLevel.SESSION),
            ("SESSION", OtelCollectLevel.SESSION),
            ("reactive_update", OtelCollectLevel.REACTIVE_UPDATE),
            ("REACTIVE_UPDATE", OtelCollectLevel.REACTIVE_UPDATE),
            ("reactivity", OtelCollectLevel.REACTIVITY),
            ("REACTIVITY", OtelCollectLevel.REACTIVITY),
            ("all", OtelCollectLevel.ALL),
            ("ALL", OtelCollectLevel.ALL),
        ],
    )
    def test_env_var_levels(self, env_value: str, expected: OtelCollectLevel) -> None:
        """Test that SHINY_OTEL_COLLECT environment variable is respected."""
        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": env_value}):
            level = get_level()
            assert level == expected

    def test_env_var_reactive_is_invalid(self):
        """Test that 'reactive' is not a supported alias; it warns and defaults to ALL."""
        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactive"}):
            with pytest.warns(UserWarning, match="Invalid SHINY_OTEL_COLLECT"):
                level = get_level()
                assert level == OtelCollectLevel.ALL

    def test_invalid_env_var_defaults_to_all(self):
        """Test that invalid env var value defaults to ALL with warning."""
        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "invalid_value"}):
            with pytest.warns(UserWarning, match="Invalid SHINY_OTEL_COLLECT"):
                level = get_level()
                assert level == OtelCollectLevel.ALL


class TestSpanWrappers:
    """Span wrapper utilities tests"""

    def test_shiny_otel_span_import(self):
        """Test that span wrapper function can be imported."""
        assert callable(shiny_otel_span)

    @pytest.mark.asyncio
    async def test_shiny_otel_span_creates_span(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that shiny_otel_span creates a span when collection is enabled."""
        _provider, _exporter = otel_tracer_provider

        # Enable tracing to allow span creation
        with patch_otel_tracing_state(tracing_enabled=True):
            async with shiny_otel_span(
                "test_span_async",
                infer_session_id=True,
                attributes={"key": "value"},
                required_level=OtelCollectLevel.SESSION,
            ) as span:
                assert span is not None
                # With session-scoped TracerProvider, span will be recording
                assert span.is_recording() is True

    @pytest.mark.asyncio
    async def test_shiny_otel_span_no_op_when_not_collecting(self):
        """Test that shiny_otel_span returns None when collection disabled."""
        # Force tracing disabled to simulate no SDK configuration
        with patch_otel_tracing_state(tracing_enabled=False):
            async with shiny_otel_span(
                "test_span_async",
                infer_session_id=True,
                attributes={"key": "value"},
                required_level=OtelCollectLevel.SESSION,
            ) as span:
                # yields None when not collecting
                assert span is None

    @pytest.mark.asyncio
    async def test_shiny_otel_span_auto_adds_session_id(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that shiny_otel_span auto-attaches session.id from active session context."""
        provider, exporter = otel_tracer_provider
        mock_session = Mock()
        mock_session.id = "session-123"
        mock_session.ns = ""

        with patch_otel_tracing_state(tracing_enabled=True):
            with session_context(mock_session):
                async with shiny_otel_span(
                    "test_span_with_session",
                    infer_session_id=True,
                    required_level=OtelCollectLevel.SESSION,
                ):
                    pass

        spans = get_exported_spans(provider, exporter)
        app_spans = [s for s in spans if s.name == "test_span_with_session"]
        assert len(app_spans) == 1
        assert app_spans[0].attributes is not None
        assert app_spans[0].attributes.get("session.id") == "session-123"
