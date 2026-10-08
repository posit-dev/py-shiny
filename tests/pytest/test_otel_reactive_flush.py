"""
OpenTelemetry Reactive Flush Instrumentation

Tests cover:
- reactive_update span creation during flush cycles
- Collection level controls for REACTIVE_UPDATE level
- Multiple flush cycles create separate spans
"""

import os
from typing import Tuple
from unittest.mock import patch

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shiny.otel._collect import OtelCollectLevel, get_level
from shiny.otel._core import is_otel_tracing_enabled
from shiny.reactive._core import ReactiveEnvironment

from .otel_helpers import get_exported_spans, patch_otel_tracing_state


class TestReactiveFlushSpans:
    """Tests for reactive_update span creation during flush cycles"""

    def test_reactive_update_collection_enabled_at_reactive_update_level(self):
        """Test that collection is enabled for REACTIVE_UPDATE level when SHINY_OTEL_COLLECT=reactive_update"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactive_update"}):
                assert (
                    is_otel_tracing_enabled()
                    and get_level() >= OtelCollectLevel.REACTIVE_UPDATE
                ) is True
                assert (
                    is_otel_tracing_enabled()
                    and get_level() >= OtelCollectLevel.REACTIVITY
                ) is False

    def test_reactive_update_collection_enabled_at_all_level(self):
        """Test that REACTIVE_UPDATE level collection is enabled when SHINY_OTEL_COLLECT=all"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                assert (
                    is_otel_tracing_enabled()
                    and get_level() >= OtelCollectLevel.REACTIVE_UPDATE
                ) is True

    def test_reactive_update_collection_disabled_at_session_level(self):
        """Test that REACTIVE_UPDATE level collection is disabled when SHINY_OTEL_COLLECT=session"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                assert (
                    is_otel_tracing_enabled()
                    and get_level() >= OtelCollectLevel.REACTIVE_UPDATE
                ) is False

    def test_collection_disabled_at_none_level(self):
        """Test that collection is disabled when SHINY_OTEL_COLLECT=none"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "none"}):
                assert (
                    is_otel_tracing_enabled()
                    and get_level() >= OtelCollectLevel.SESSION
                ) is False
                assert (
                    is_otel_tracing_enabled()
                    and get_level() >= OtelCollectLevel.REACTIVE_UPDATE
                ) is False


class TestReactiveFlushInstrumentation:
    """Tests for reactive_update span instrumentation in flush cycles"""

    @pytest.mark.asyncio
    async def test_flush_creates_no_reactive_update_span(
        self, otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter]
    ):
        """A flush can serve several sessions, so it has no span of its own; each
        session's `reactive_update` span follows its cycle (see
        `test_otel_reactive_update.py`)."""
        provider, memory_exporter = otel_tracer_provider
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                env = ReactiveEnvironment()
                await env.run_round()

        spans = get_exported_spans(provider, memory_exporter)
        assert not [s for s in spans if s.name == "reactive_update"]

    @pytest.mark.asyncio
    async def test_flush_no_span_when_not_collecting(self):
        """Test that flush() does not create span when not collecting"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                # Create a reactive environment
                env = ReactiveEnvironment()

                # Mock the tracer to verify it's not called at span creation level
                with patch("shiny.otel._core.get_otel_tracer") as mock_get_tracer:
                    await env.run_round()

                    # Tracer should not be retrieved since collection level is too low
                    mock_get_tracer.assert_not_called()
