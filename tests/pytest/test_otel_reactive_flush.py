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

from shiny.otel import OtelCollectLevel, should_otel_collect
from shiny.otel._span_wrappers import with_otel_span_async
from shiny.reactive._core import ReactiveEnvironment

from .otel_helpers import (
    otel_tracer_provider_context,
    patch_otel_tracing_state,
)


class TestReactiveFlushSpans:
    """Tests for reactive.update span creation during flush cycles"""

    def test_reactive_update_collection_enabled_at_reactive_update_level(self):
        """Test that collection is enabled for REACTIVE_UPDATE level when SHINY_OTEL_COLLECT=reactive_update"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactive_update"}):
                assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE) is True
                assert should_otel_collect(OtelCollectLevel.REACTIVITY) is False

    def test_reactive_update_collection_enabled_at_all_level(self):
        """Test that REACTIVE_UPDATE level collection is enabled when SHINY_OTEL_COLLECT=all"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE) is True

    def test_reactive_update_collection_disabled_at_session_level(self):
        """Test that REACTIVE_UPDATE level collection is disabled when SHINY_OTEL_COLLECT=session"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE) is False

    def test_collection_disabled_at_none_level(self):
        """Test that collection is disabled when SHINY_OTEL_COLLECT=none"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "none"}):
                assert should_otel_collect(OtelCollectLevel.SESSION) is False
                assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE) is False


class TestReactiveFlushInstrumentation:
    """Tests for reactive.update span instrumentation in flush cycles"""

    @pytest.mark.asyncio
    async def test_flush_creates_span_when_collecting(self):
        """Test that flush() wraps execution in reactive.update span when collecting"""
        with patch_otel_tracing_state(tracing_enabled=True):
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
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                # Create a reactive environment
                env = ReactiveEnvironment()

                # Mock the tracer to verify it's not called at span creation level
                with patch("shiny.otel._core.get_otel_tracer") as mock_get_tracer:
                    await env.flush()

                    # Tracer should not be retrieved since collection level is too low
                    mock_get_tracer.assert_not_called()

    @pytest.mark.asyncio
    async def test_contextvar_stores_span_during_flush(self):
        """Test that the current span is stored on instance during flush"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactive_update"}):
                env = ReactiveEnvironment()

                # Mock span
                mock_span = Mock()
                mock_span.__aenter__ = AsyncMock(return_value=mock_span)
                mock_span.__aexit__ = AsyncMock(return_value=None)

                # Track what span is set on instance
                captured_span = None

                async def capture_span():
                    nonlocal captured_span
                    captured_span = env._current_otel_span

                # Register callback to capture span during flush
                env.on_flushed(capture_span, once=True)

                with patch(
                    "shiny.otel._span_wrappers.with_otel_span_async",
                    return_value=mock_span,
                ):
                    await env.flush()

                # Verify span was set on instance during flush
                assert captured_span is mock_span

    @pytest.mark.asyncio
    async def test_contextvar_reset_after_flush(self):
        """Test that instance span is reset after flush completes"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactive_update"}):
                env = ReactiveEnvironment()

                # Mock span
                mock_span = Mock()
                mock_span.__aenter__ = AsyncMock(return_value=mock_span)
                mock_span.__aexit__ = AsyncMock(return_value=None)

                # Verify instance span is None before flush
                assert env._current_otel_span is None

                with patch(
                    "shiny.otel._span_wrappers.with_otel_span_async",
                    return_value=mock_span,
                ):
                    await env.flush()

                # Verify instance span is reset to None after flush
                assert env._current_otel_span is None

    @pytest.mark.asyncio
    async def test_span_parent_child_relationship(self):
        """Test that reactive.update span is child of parent span when nested"""
        with otel_tracer_provider_context() as (_, memory_exporter):
            with patch_otel_tracing_state(tracing_enabled=True):
                with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                    # Simulate session.start with reactive_flush inside
                    async with with_otel_span_async(
                        "session.start",
                        {"session.id": "test123"},
                        level=OtelCollectLevel.SESSION,
                    ):
                        # Create reactive environment and flush
                        env = ReactiveEnvironment()
                        await env.flush()

            # Get exported spans
            spans = memory_exporter.get_finished_spans()

            # Filter out the _otel_is_recording span
            app_spans = [s for s in spans if not s.name.startswith("_otel")]

            # Should have 2 spans: session.start and reactive.update
            assert len(app_spans) >= 2

            # Find session.start and reactive.update spans
            session_span = next((s for s in app_spans if s.name == "session.start"), None)
            reactive_span = next(
                (s for s in app_spans if s.name == "reactive.update"), None
            )

            assert session_span is not None, "session.start span should exist"
            assert reactive_span is not None, "reactive.update span should exist"

            # Verify parent-child relationship
            assert reactive_span.parent is not None, "reactive.update should have a parent"
            assert reactive_span.context is not None, "reactive.update should have context"
            assert session_span.context is not None, "session.start should have context"
            assert (
                reactive_span.parent.span_id == session_span.context.span_id
            ), "reactive.update parent should be session.start"

            # Verify they're in the same trace
            assert (
                reactive_span.context.trace_id == session_span.context.trace_id
            ), "Spans should be in same trace"
