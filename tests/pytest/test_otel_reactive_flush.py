"""
OpenTelemetry Reactive Flush Instrumentation

Tests cover:
- reactive.update span creation during flush cycles
- Collection level controls for REACTIVE_UPDATE level
- Contextvar storage of spans for child reactive spans
- Multiple flush cycles create separate spans
"""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from shiny.otel import OtelCollectLevel


class TestReactiveFlushSpans:
    """Tests for reactive.update span creation during flush cycles"""

    def test_reactive_update_collection_enabled_at_reactive_update_level(self):
        """Test that collection is enabled for REACTIVE_UPDATE level when SHINY_OTEL_COLLECT=reactive_update"""
        from shiny.otel import should_otel_collect

        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactive_update"}):
                assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE) is True
                assert should_otel_collect(OtelCollectLevel.REACTIVITY) is False

    def test_reactive_update_collection_enabled_at_all_level(self):
        """Test that REACTIVE_UPDATE level collection is enabled when SHINY_OTEL_COLLECT=all"""
        from shiny.otel import should_otel_collect

        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE) is True

    def test_reactive_update_collection_disabled_at_session_level(self):
        """Test that REACTIVE_UPDATE level collection is disabled when SHINY_OTEL_COLLECT=session"""
        from shiny.otel import should_otel_collect

        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE) is False

    def test_collection_disabled_at_none_level(self):
        """Test that collection is disabled when SHINY_OTEL_COLLECT=none"""
        from shiny.otel import should_otel_collect

        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "none"}):
                assert should_otel_collect(OtelCollectLevel.SESSION) is False
                assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE) is False


class TestReactiveFlushInstrumentation:
    """Tests for reactive.update span instrumentation in flush cycles"""

    @pytest.mark.asyncio
    async def test_flush_creates_span_when_collecting(self):
        """Test that flush() wraps execution in reactive.update span when collecting"""
        from shiny.reactive._core import ReactiveEnvironment

        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactive_update"}):
                # Create a reactive environment
                env = ReactiveEnvironment()

                # Mock the tracer and span
                mock_span = Mock()
                mock_span.__aenter__ = AsyncMock(return_value=mock_span)
                mock_span.__aexit__ = AsyncMock(return_value=None)

                with patch(
                    "shiny.otel._span_wrappers.with_otel_span_async",
                    return_value=mock_span,
                ) as mock_wrapper:
                    await env.flush()

                    # Verify with_otel_span_async was called with correct parameters
                    mock_wrapper.assert_called_once()
                    args, kwargs = mock_wrapper.call_args
                    assert args[0] == "reactive.update"
                    assert kwargs["level"] == OtelCollectLevel.REACTIVE_UPDATE

    @pytest.mark.asyncio
    async def test_flush_no_span_when_not_collecting(self):
        """Test that flush() does not create span when not collecting"""
        from shiny.reactive._core import ReactiveEnvironment

        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                # Create a reactive environment
                env = ReactiveEnvironment()

                # Mock the tracer to verify it's not called at span creation level
                with patch(
                    "shiny.otel._core.get_otel_tracer"
                ) as mock_get_tracer:
                    await env.flush()

                    # Tracer should not be retrieved since collection level is too low
                    mock_get_tracer.assert_not_called()

    @pytest.mark.asyncio
    async def test_contextvar_stores_span_during_flush(self):
        """Test that the current span is stored in contextvar during flush"""
        from shiny.reactive._core import (
            ReactiveEnvironment,
            _current_reactive_update_span,
        )

        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactive_update"}):
                env = ReactiveEnvironment()

                # Mock span
                mock_span = Mock()
                mock_span.__aenter__ = AsyncMock(return_value=mock_span)
                mock_span.__aexit__ = AsyncMock(return_value=None)

                # Track what span is set in contextvar
                captured_span = None

                async def capture_span():
                    nonlocal captured_span
                    captured_span = _current_reactive_update_span.get()

                # Register callback to capture span during flush
                env.on_flushed(capture_span, once=True)

                with patch(
                    "shiny.otel._span_wrappers.with_otel_span_async",
                    return_value=mock_span,
                ):
                    await env.flush()

                # Verify span was set in contextvar during flush
                assert captured_span is mock_span

    @pytest.mark.asyncio
    async def test_contextvar_reset_after_flush(self):
        """Test that contextvar is reset after flush completes"""
        from shiny.reactive._core import (
            ReactiveEnvironment,
            _current_reactive_update_span,
        )

        with patch("shiny.otel._core._tracing_enabled", True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactive_update"}):
                env = ReactiveEnvironment()

                # Mock span
                mock_span = Mock()
                mock_span.__aenter__ = AsyncMock(return_value=mock_span)
                mock_span.__aexit__ = AsyncMock(return_value=None)

                # Verify contextvar is None before flush
                assert _current_reactive_update_span.get() is None

                with patch(
                    "shiny.otel._span_wrappers.with_otel_span_async",
                    return_value=mock_span,
                ):
                    await env.flush()

                # Verify contextvar is reset to None after flush
                assert _current_reactive_update_span.get() is None
