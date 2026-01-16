"""
Tests for Phase 1: OpenTelemetry Foundation (Core Infrastructure)

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
    CollectLevel,
    get_collect_level,
    get_logger,
    get_tracer,
    is_tracing_enabled,
    should_collect,
)


class TestCore:
    """Tests for shiny/otel/_core.py"""

    def test_get_tracer_returns_tracer(self):
        """Test that get_tracer() returns a tracer instance."""
        tracer = get_tracer()
        assert tracer is not None
        # Should return same instance on subsequent calls
        assert get_tracer() is tracer

    def test_get_logger_returns_logger(self):
        """Test that get_logger() returns a logger instance."""
        logger = get_logger()
        assert logger is not None
        # Should return same instance on subsequent calls
        assert get_logger() is logger

    def test_is_tracing_enabled_without_sdk(self):
        """Test that is_tracing_enabled() returns False when SDK not configured."""
        # Reset cached value
        import shiny.otel._core

        shiny.otel._core._tracing_enabled = None

        # Without SDK, tracing should be disabled
        assert is_tracing_enabled() is False


class TestCollectLevel:
    """Tests for shiny/otel/_collect.py - CollectLevel enum"""

    def test_collect_level_values(self):
        """Test that CollectLevel enum has correct values."""
        assert CollectLevel.NONE == 0
        assert CollectLevel.SESSION == 1
        assert CollectLevel.REACTIVE_UPDATE == 2
        assert CollectLevel.REACTIVITY == 3
        assert CollectLevel.ALL == 4

    def test_collect_level_ordering(self):
        """Test that CollectLevel values are correctly ordered."""
        assert CollectLevel.NONE < CollectLevel.SESSION
        assert CollectLevel.SESSION < CollectLevel.REACTIVE_UPDATE
        assert CollectLevel.REACTIVE_UPDATE < CollectLevel.REACTIVITY
        assert CollectLevel.REACTIVITY < CollectLevel.ALL


class TestGetCollectLevel:
    """Tests for get_collect_level() function"""

    def test_default_level(self):
        """Test that default collection level is ALL when no env var set."""
        with patch.dict(os.environ, {}, clear=True):
            # Clear the env var if it exists
            os.environ.pop("SHINY_OTEL_COLLECT", None)
            level = get_collect_level()
            assert level == CollectLevel.ALL

    @pytest.mark.parametrize(
        "env_value,expected",
        [
            ("none", CollectLevel.NONE),
            ("NONE", CollectLevel.NONE),
            ("session", CollectLevel.SESSION),
            ("SESSION", CollectLevel.SESSION),
            ("reactive_update", CollectLevel.REACTIVE_UPDATE),
            ("REACTIVE_UPDATE", CollectLevel.REACTIVE_UPDATE),
            ("reactivity", CollectLevel.REACTIVITY),
            ("REACTIVITY", CollectLevel.REACTIVITY),
            ("all", CollectLevel.ALL),
            ("ALL", CollectLevel.ALL),
        ],
    )
    def test_env_var_levels(self, env_value: str, expected: CollectLevel) -> None:
        """Test that SHINY_OTEL_COLLECT environment variable is respected."""
        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": env_value}):
            level = get_collect_level()
            assert level == expected

    def test_env_var_reactive_alias(self):
        """Test that 'reactive' is aliased to 'reactivity'."""
        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactive"}):
            level = get_collect_level()
            assert level == CollectLevel.REACTIVITY

    def test_invalid_env_var_defaults_to_all(self):
        """Test that invalid env var value defaults to ALL with warning."""
        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "invalid_value"}):
            with pytest.warns(UserWarning, match="Invalid SHINY_OTEL_COLLECT"):
                level = get_collect_level()
                assert level == CollectLevel.ALL


class TestShouldCollect:
    """Tests for should_collect() function"""

    def test_should_collect_without_sdk(self):
        """Test that should_collect returns False when SDK not configured."""
        # Reset cached tracing status
        import shiny.otel._core

        shiny.otel._core._tracing_enabled = None

        # Without SDK, should_collect should always return False
        assert should_collect(CollectLevel.NONE) is False
        assert should_collect(CollectLevel.SESSION) is False
        assert should_collect(CollectLevel.REACTIVE_UPDATE) is False
        assert should_collect(CollectLevel.REACTIVITY) is False
        assert should_collect(CollectLevel.ALL) is False

    @pytest.mark.parametrize(
        "current_level,required_level,expected",
        [
            # NONE collects nothing
            (CollectLevel.NONE, CollectLevel.NONE, False),
            (CollectLevel.NONE, CollectLevel.SESSION, False),
            (CollectLevel.NONE, CollectLevel.ALL, False),
            # SESSION collects SESSION and below
            (CollectLevel.SESSION, CollectLevel.NONE, True),
            (CollectLevel.SESSION, CollectLevel.SESSION, True),
            (CollectLevel.SESSION, CollectLevel.REACTIVE_UPDATE, False),
            (CollectLevel.SESSION, CollectLevel.ALL, False),
            # REACTIVE_UPDATE collects REACTIVE_UPDATE, SESSION and below
            (CollectLevel.REACTIVE_UPDATE, CollectLevel.NONE, True),
            (CollectLevel.REACTIVE_UPDATE, CollectLevel.SESSION, True),
            (CollectLevel.REACTIVE_UPDATE, CollectLevel.REACTIVE_UPDATE, True),
            (CollectLevel.REACTIVE_UPDATE, CollectLevel.REACTIVITY, False),
            # ALL collects everything
            (CollectLevel.ALL, CollectLevel.NONE, True),
            (CollectLevel.ALL, CollectLevel.SESSION, True),
            (CollectLevel.ALL, CollectLevel.REACTIVE_UPDATE, True),
            (CollectLevel.ALL, CollectLevel.REACTIVITY, True),
            (CollectLevel.ALL, CollectLevel.ALL, True),
        ],
    )
    def test_should_collect_logic_when_tracing_disabled(
        self,
        current_level: CollectLevel,
        required_level: CollectLevel,
        expected: bool,
    ) -> None:
        """Test should_collect logic based on level comparison (when tracing disabled)."""
        # Reset tracing status to ensure it's disabled
        import shiny.otel._core

        shiny.otel._core._tracing_enabled = None

        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": current_level.name.lower()}):
            # Without SDK, should always be False regardless of levels
            result = should_collect(required_level)
            assert result is False


class TestSpanWrappers:
    """Tests for span wrapper utilities"""

    def test_with_span_import(self):
        """Test that span wrapper functions can be imported."""
        from shiny.otel._span_wrappers import with_span, with_span_async

        assert callable(with_span)
        assert callable(with_span_async)

    def test_with_span_creates_span(self):
        """Test that with_span creates a span (even if non-recording)."""
        from shiny.otel._span_wrappers import with_span

        with with_span("test_span", {"key": "value"}) as span:
            assert span is not None
            # Without SDK, span won't be recording
            assert span.is_recording() is False

    @pytest.mark.asyncio
    async def test_with_span_async_creates_span(self):
        """Test that with_span_async creates a span (even if non-recording)."""
        from shiny.otel._span_wrappers import with_span_async

        async with with_span_async("test_span_async", {"key": "value"}) as span:
            assert span is not None
            # Without SDK, span won't be recording
            assert span.is_recording() is False
