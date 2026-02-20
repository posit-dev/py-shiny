"""
OpenTelemetry Foundation (Core Infrastructure)

Tests cover:
- Lazy tracer/logger initialization
- Collection level management
- Environment variable configuration
- No-op behavior when SDK not configured
"""

import os
from unittest.mock import patch

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shiny.otel._collect import OtelCollectLevel, get_otel_collect_level
from shiny.otel._core import get_otel_logger, get_otel_tracer, is_otel_tracing_enabled
from shiny.otel._span_wrappers import shiny_otel_span_async

from .otel_helpers import patch_otel_tracing_state


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
    """get_otel_collect_level() function tests"""

    def test_default_level(self):
        """Test that default collection level is ALL when no env var set."""
        with patch.dict(os.environ, {}, clear=True):
            # Clear the env var if it exists
            os.environ.pop("SHINY_OTEL_COLLECT", None)
            level = get_otel_collect_level()
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
            level = get_otel_collect_level()
            assert level == expected

    def test_env_var_reactive_alias(self):
        """Test that 'reactive' is aliased to 'reactivity'."""
        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactive"}):
            level = get_otel_collect_level()
            assert level == OtelCollectLevel.REACTIVITY

    def test_invalid_env_var_defaults_to_all(self):
        """Test that invalid env var value defaults to ALL with warning."""
        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "invalid_value"}):
            with pytest.warns(UserWarning, match="Invalid SHINY_OTEL_COLLECT"):
                level = get_otel_collect_level()
                assert level == OtelCollectLevel.ALL


class TestSpanWrappers:
    """Span wrapper utilities tests"""

    def test_shiny_otel_span_async_import(self):
        """Test that span wrapper function can be imported."""
        assert callable(shiny_otel_span_async)

    @pytest.mark.asyncio
    async def test_shiny_otel_span_async_creates_span(
        self, otel_tracer_provider: tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that shiny_otel_span_async creates a span when collection is enabled."""
        _provider, _exporter = otel_tracer_provider

        # Enable tracing to allow span creation
        with patch_otel_tracing_state(tracing_enabled=True):
            async with shiny_otel_span_async(
                "test_span_async",
                attributes={"key": "value"},
                required_level=OtelCollectLevel.SESSION,
            ) as span:
                assert span is not None
                # With session-scoped TracerProvider, span will be recording
                assert span.is_recording() is True

    @pytest.mark.asyncio
    async def test_shiny_otel_span_async_no_op_when_not_collecting(self):
        """Test that shiny_otel_span_async returns None when collection disabled."""
        # Force tracing disabled to simulate no SDK configuration
        with patch_otel_tracing_state(tracing_enabled=False):
            async with shiny_otel_span_async(
                "test_span_async",
                attributes={"key": "value"},
                required_level=OtelCollectLevel.SESSION,
            ) as span:
                # yields None when not collecting
                assert span is None
