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

from shiny.otel import (
    OtelCollectLevel,
    get_otel_collect_level,
    get_otel_logger,
    get_otel_tracer,
    is_otel_tracing_enabled,
    should_otel_collect,
)
from shiny.otel._span_wrappers import with_otel_span, with_otel_span_async

from .test_otel_helpers import patch_otel_tracing_state, reset_otel_tracing_state


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
        # Reset cached value
        reset_otel_tracing_state()

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


class TestShouldOtelCollect:
    """should_otel_collect() function tests"""

    def test_should_otel_collect_without_sdk(self):
        """Test that should_otel_collect returns False when SDK not configured."""
        # Reset cached tracing status
        reset_otel_tracing_state()

        # Without SDK, should_otel_collect should always return False
        # (except for NONE which should raise ValueError)
        assert should_otel_collect(OtelCollectLevel.SESSION) is False
        assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE) is False
        assert should_otel_collect(OtelCollectLevel.REACTIVITY) is False
        assert should_otel_collect(OtelCollectLevel.ALL) is False

    def test_should_otel_collect_raises_on_none(self):
        """Test that should_otel_collect raises ValueError when called with NONE."""
        with pytest.raises(
            ValueError,
            match="should_otel_collect\\(\\) cannot be called with OtelCollectLevel.NONE",
        ):
            should_otel_collect(OtelCollectLevel.NONE)

    @pytest.mark.parametrize(
        "current_level,required_level,expected",
        [
            # NONE collects nothing (current_level can be NONE, but required_level cannot)
            (OtelCollectLevel.NONE, OtelCollectLevel.SESSION, False),
            (OtelCollectLevel.NONE, OtelCollectLevel.ALL, False),
            # SESSION collects SESSION only
            (OtelCollectLevel.SESSION, OtelCollectLevel.SESSION, True),
            (OtelCollectLevel.SESSION, OtelCollectLevel.REACTIVE_UPDATE, False),
            (OtelCollectLevel.SESSION, OtelCollectLevel.ALL, False),
            # REACTIVE_UPDATE collects REACTIVE_UPDATE and SESSION
            (OtelCollectLevel.REACTIVE_UPDATE, OtelCollectLevel.SESSION, True),
            (OtelCollectLevel.REACTIVE_UPDATE, OtelCollectLevel.REACTIVE_UPDATE, True),
            (OtelCollectLevel.REACTIVE_UPDATE, OtelCollectLevel.REACTIVITY, False),
            # ALL collects everything
            (OtelCollectLevel.ALL, OtelCollectLevel.SESSION, True),
            (OtelCollectLevel.ALL, OtelCollectLevel.REACTIVE_UPDATE, True),
            (OtelCollectLevel.ALL, OtelCollectLevel.REACTIVITY, True),
            (OtelCollectLevel.ALL, OtelCollectLevel.ALL, True),
        ],
    )
    def test_should_otel_collect_logic_when_tracing_disabled(
        self,
        current_level: OtelCollectLevel,
        required_level: OtelCollectLevel,
        expected: bool,
    ) -> None:
        """Test should_otel_collect logic based on level comparison (when tracing disabled)."""
        # Reset tracing status to ensure it's disabled
        reset_otel_tracing_state()

        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": current_level.name.lower()}):
            # Without SDK, should always be False regardless of levels
            result = should_otel_collect(required_level)
            assert result is False


class TestSpanWrappers:
    """Span wrapper utilities tests"""

    def test_with_otel_span_import(self):
        """Test that span wrapper functions can be imported."""
        assert callable(with_otel_span)
        assert callable(with_otel_span_async)

    def test_with_otel_span_creates_span(self):
        """Test that with_otel_span creates a span when collection is enabled."""
        # Force collection by mocking should_otel_collect at its source
        with patch("shiny.otel._collect.should_otel_collect", return_value=True):
            with with_otel_span(
                "test_span", {"key": "value"}, level=OtelCollectLevel.SESSION
            ) as span:
                assert span is not None
                # Without SDK, span won't be recording
                assert span.is_recording() is False

    @pytest.mark.asyncio
    async def test_with_otel_span_async_creates_span(self):
        """Test that with_otel_span_async creates a span when collection is enabled."""
        # Force collection by mocking should_otel_collect at its source
        with patch("shiny.otel._collect.should_otel_collect", return_value=True):
            async with with_otel_span_async(
                "test_span_async", {"key": "value"}, level=OtelCollectLevel.SESSION
            ) as span:
                assert span is not None
                # Without SDK, span won't be recording
                assert span.is_recording() is False

    def test_with_otel_span_no_op_when_not_collecting(self):
        """Test that with_otel_span returns None when collection disabled."""
        # Without SDK configured, should return None (no-op)
        with patch_otel_tracing_state(tracing_enabled=None):
            with with_otel_span(
                "test_span", {"key": "value"}, level=OtelCollectLevel.SESSION
            ) as span:
                # yields None when not collecting
                assert span is None

    @pytest.mark.asyncio
    async def test_with_otel_span_async_no_op_when_not_collecting(self):
        """Test that with_otel_span_async returns None when collection disabled."""
        # Without SDK configured, should return None (no-op)
        with patch_otel_tracing_state(tracing_enabled=None):
            async with with_otel_span_async(
                "test_span_async", {"key": "value"}, level=OtelCollectLevel.SESSION
            ) as span:
                # yields None when not collecting
                assert span is None
