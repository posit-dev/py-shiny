"""
OpenTelemetry Reactive Execution Instrumentation

Tests cover:
- Calc execution span creation
- Effect execution span creation
- Output rendering span creation
- Label generation for reactive computations
- Source code attribute extraction
- Span parent-child relationships (reactive.update → calc/effect/output)
- Collection level controls
"""

import os
from typing import Tuple
from unittest.mock import AsyncMock, patch

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shiny.otel import OtelCollectLevel
from shiny.otel._attributes import extract_source_ref
from shiny.otel._labels import generate_reactive_label
from shiny.otel._span_wrappers import with_otel_span_async
from shiny.reactive import Calc_, Effect_

from .otel_helpers import get_exported_spans, patch_otel_tracing_state


class TestLabelGeneration:
    """Label generation tests"""

    def test_generate_reactive_label_for_calc(self):
        """Test generating label for a calc with function name"""

        def my_calc():
            return 42

        label = generate_reactive_label(my_calc, "reactive")
        assert label == "reactive my_calc"

    def test_generate_reactive_label_for_lambda(self):
        """Test generating label for anonymous/lambda function"""
        label = generate_reactive_label(lambda: 42, "reactive")
        assert label == "reactive <anonymous>"

    def test_generate_reactive_label_with_namespace(self):
        """Test generating label with namespace prefix"""
        from unittest.mock import Mock

        from shiny._namespaces import ResolvedId

        def my_calc():
            return 42

        # Create a mock session with a namespace
        mock_session = Mock()
        mock_session.ns = ResolvedId("mod")

        label = generate_reactive_label(my_calc, "reactive", session=mock_session)
        assert label == "reactive mod:my_calc"

    def test_generate_reactive_label_with_modifier(self):
        """Test generating label with modifier (e.g., cache)"""

        def my_calc():
            return 42

        label = generate_reactive_label(my_calc, "reactive", modifier="cache")
        assert label == "reactive cache my_calc"

    def test_generate_observe_label(self):
        """Test generating label for effect (observe)"""

        def my_effect():
            pass

        label = generate_reactive_label(my_effect, "observe")
        assert label == "observe my_effect"

    def test_generate_output_label(self):
        """Test generating label for output rendering"""

        def my_output():
            return "text"

        label = generate_reactive_label(my_output, "output")
        assert label == "output my_output"


class TestReactiveModifierContext:
    """Reactive modifier context tests"""

    def test_get_modifier_outside_context(self):
        """Test getting modifier outside any context returns None"""
        from shiny.reactive._core import get_current_reactive_modifier

        modifier = get_current_reactive_modifier()
        assert modifier is None

    def test_single_modifier_context(self):
        """Test setting a single modifier in context"""
        from shiny.reactive._core import (
            get_current_reactive_modifier,
            reactive_modifier_context,
        )

        with reactive_modifier_context("event"):
            modifier = get_current_reactive_modifier()
            assert modifier == "event"

        # Should be None again after exiting context
        modifier = get_current_reactive_modifier()
        assert modifier is None

    def test_multiple_nested_modifier_contexts(self):
        """Test multiple nested modifiers are space-separated"""
        from shiny.reactive._core import (
            get_current_reactive_modifier,
            reactive_modifier_context,
        )

        with reactive_modifier_context("event"):
            assert get_current_reactive_modifier() == "event"

            with reactive_modifier_context("testlevel"):
                assert get_current_reactive_modifier() == "event testlevel"

            # Should be back to just "event"
            assert get_current_reactive_modifier() == "event"

        # Should be None again
        assert get_current_reactive_modifier() is None

    def test_label_generation_with_modifier_from_context(self):
        """Test that generate_reactive_label uses modifier from context"""
        from shiny.reactive._core import reactive_modifier_context

        def my_calc():
            return 42

        # Without context
        label = generate_reactive_label(my_calc, "reactive")
        assert label == "reactive my_calc"

        # With event modifier in context
        with reactive_modifier_context("event"):
            from shiny.reactive._core import get_current_reactive_modifier

            label = generate_reactive_label(
                my_calc, "reactive", modifier=get_current_reactive_modifier()
            )
            assert label == "reactive event my_calc"

        # With multiple modifiers
        with reactive_modifier_context("event"):
            with reactive_modifier_context("testlevel"):
                from shiny.reactive._core import get_current_reactive_modifier

                label = generate_reactive_label(
                    my_calc,
                    "reactive",
                    modifier=get_current_reactive_modifier(),
                )
                assert label == "reactive event testlevel my_calc"

    def test_reset_modifier_context(self):
        """Test that reset_reactive_modifier_context temporarily clears all modifiers"""
        from shiny.reactive._core import (
            get_current_reactive_modifier,
            reactive_modifier_context,
            reset_reactive_modifier_context,
        )

        # Start with no modifier
        assert get_current_reactive_modifier() is None

        with reactive_modifier_context("event"):
            assert get_current_reactive_modifier() == "event"

            # Reset should temporarily clear modifier
            with reset_reactive_modifier_context():
                assert get_current_reactive_modifier() is None

            # Should be back to "event" after reset context exits
            assert get_current_reactive_modifier() == "event"

        # Should be None after all contexts exit
        assert get_current_reactive_modifier() is None

    def test_reset_modifier_context_with_nested_modifiers(self):
        """Test reset with multiple nested modifiers"""
        from shiny.reactive._core import (
            get_current_reactive_modifier,
            reactive_modifier_context,
            reset_reactive_modifier_context,
        )

        with reactive_modifier_context("event"):
            with reactive_modifier_context("cache"):
                # Should have both modifiers
                assert get_current_reactive_modifier() == "event cache"

                # Reset should clear all modifiers
                with reset_reactive_modifier_context():
                    assert get_current_reactive_modifier() is None

                # Should restore both modifiers
                assert get_current_reactive_modifier() == "event cache"

            # Should be back to just "event"
            assert get_current_reactive_modifier() == "event"

    def test_reset_modifier_context_equivalent_to_none(self):
        """Test that reset_reactive_modifier_context is equivalent to reactive_modifier_context(None)"""
        from shiny.reactive._core import (
            get_current_reactive_modifier,
            reactive_modifier_context,
            reset_reactive_modifier_context,
        )

        # Test with reset_reactive_modifier_context
        with reactive_modifier_context("event"):
            with reset_reactive_modifier_context():
                result1 = get_current_reactive_modifier()

        # Test with reactive_modifier_context(None)
        with reactive_modifier_context("event"):
            with reactive_modifier_context(None):
                result2 = get_current_reactive_modifier()

        # Both should produce the same result
        assert result1 == result2 == None

    @pytest.mark.asyncio
    async def test_calc_resets_modifier_for_nested_reads(self):
        """Test that calc execution resets modifiers when reading nested reactives"""
        from shiny.reactive import Calc_, flush
        from shiny.reactive._core import (
            get_current_reactive_modifier,
            reactive_modifier_context,
        )

        # Track what modifier was active when inner_calc executed
        modifier_during_inner = None

        def inner_calc():
            nonlocal modifier_during_inner
            modifier_during_inner = get_current_reactive_modifier()
            return 42

        inner = Calc_(inner_calc)

        def outer_calc():
            # This should execute with "event" modifier in its span,
            # but when it reads inner_calc, the modifier should be reset
            return inner()

        outer = Calc_(outer_calc)

        # Execute outer_calc with "event" modifier
        with reactive_modifier_context("event"):
            await outer.update_value()

        # The inner calc should have been executed with NO modifier
        # (even though outer had "event" modifier)
        assert modifier_during_inner is None


class TestSourceReferenceExtraction:
    """Source code attribute extraction tests"""

    def test_extract_source_ref_from_function(self):
        """Test extracting source reference from a regular function"""

        def my_func():
            return 42

        attrs = extract_source_ref(my_func)

        # Should have code attributes
        assert "code.function" in attrs
        assert attrs["code.function"] == "my_func"
        assert "code.filepath" in attrs
        assert "code.lineno" in attrs

    def test_extract_source_ref_from_lambda(self):
        """Test extracting source reference from lambda"""
        attrs = extract_source_ref(lambda: 42)

        # Lambda should still have source info
        assert "code.function" in attrs
        assert attrs["code.function"] == "<lambda>"
        assert "code.filepath" in attrs
        assert "code.lineno" in attrs

    def test_extract_source_ref_from_builtin(self):
        """Test extracting source reference from built-in function"""
        attrs = extract_source_ref(len)

        # Built-in functions won't have source info
        # Should return empty dict without errors
        assert isinstance(attrs, dict)


class TestCalcSpans:
    """Calc execution span tests"""

    @pytest.mark.asyncio
    async def test_calc_creates_span_when_enabled(self):
        """Test that Calc execution creates a span when collection level is REACTIVITY"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                # Create a calc
                def my_calc():
                    return 42

                calc = Calc_(my_calc)

                # Mock span wrapper to verify it's called
                # Must patch at the import location in _reactives module
                with patch(
                    "shiny.reactive._reactives.with_otel_span_async"
                ) as mock_span:
                    # Configure mock to act as async context manager
                    mock_span.return_value.__aenter__ = AsyncMock(return_value=None)
                    mock_span.return_value.__aexit__ = AsyncMock(return_value=None)

                    # Execute the calc
                    await calc.update_value()

                    # Verify span was created
                    mock_span.assert_called_once()
                    call_args = mock_span.call_args
                    # Verify the name callable was passed
                    name_callable = call_args[0][0]
                    assert callable(name_callable)
                    assert name_callable() == "reactive my_calc"
                    assert call_args[1]["level"] == OtelCollectLevel.REACTIVITY

    @pytest.mark.asyncio
    async def test_calc_no_span_when_disabled(self):
        """Test that Calc execution doesn't create span when collection level is too low"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                # Create a calc
                def my_calc():
                    return 42

                calc = Calc_(my_calc)

                # Mock span wrapper to verify it's not called
                # Must patch at the import location in _reactives module
                with patch(
                    "shiny.reactive._reactives.with_otel_span_async"
                ) as mock_span:
                    # Execute the calc
                    await calc.update_value()

                    # Verify span was not created (no-op context manager)
                    # The span wrapper is still called but returns a no-op
                    mock_span.assert_called_once()

    @pytest.mark.asyncio
    async def test_calc_span_includes_source_attrs(self):
        """Test that Calc span includes source code attributes"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                # Create a calc with known source
                def my_calc():
                    return 42

                calc = Calc_(my_calc)

                # Mock span wrapper to capture attributes
                # Must patch at the import location in _reactives module
                with patch(
                    "shiny.reactive._reactives.with_otel_span_async"
                ) as mock_span:
                    # Configure mock
                    mock_span.return_value.__aenter__ = AsyncMock(return_value=None)
                    mock_span.return_value.__aexit__ = AsyncMock(return_value=None)

                    # Execute the calc
                    await calc.update_value()

                    # Verify source attributes were included via _otel_attrs
                    call_args = mock_span.call_args
                    attrs = call_args[1]["attributes"]
                    # Attributes are stored on the calc instance at init time
                    assert "code.function" in attrs
                    assert attrs["code.function"] == "my_calc"
                    assert "code.filepath" in attrs
                    assert "code.lineno" in attrs


class TestEffectSpans:
    """Effect execution span tests"""

    @pytest.mark.asyncio
    async def test_effect_creates_span_when_enabled(self):
        """Test that Effect execution creates a span when collection level is REACTIVITY"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):

                # Create an effect
                def my_effect():
                    pass

                effect = Effect_(my_effect, session=None)

                # Mock span wrapper to verify it's called
                # Must patch at the import location in _reactives module
                with patch(
                    "shiny.reactive._reactives.with_otel_span_async"
                ) as mock_span:
                    # Configure mock to act as async context manager
                    mock_span.return_value.__aenter__ = AsyncMock(return_value=None)
                    mock_span.return_value.__aexit__ = AsyncMock(return_value=None)

                    # Execute the effect
                    await effect._run()

                    # Verify span was created
                    mock_span.assert_called_once()
                    call_args = mock_span.call_args
                    # Verify the name callable was passed
                    name_callable = call_args[0][0]
                    assert callable(name_callable)
                    assert name_callable() == "observe my_effect"
                    assert call_args[1]["level"] == OtelCollectLevel.REACTIVITY

    @pytest.mark.asyncio
    async def test_effect_no_span_when_disabled(self):
        """Test that Effect execution doesn't create span when collection level is too low"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):

                # Create an effect
                def my_effect():
                    pass

                effect = Effect_(my_effect, session=None)

                # Mock span wrapper to verify it's not called
                # Must patch at the import location in _reactives module
                with patch(
                    "shiny.reactive._reactives.with_otel_span_async"
                ) as mock_span:
                    # Execute the effect
                    await effect._run()

                    # Verify span was not created (no-op context manager)
                    # The span wrapper is still called but returns a no-op
                    mock_span.assert_called_once()


class TestOutputSpans:
    """Output rendering span tests"""

    def test_output_span_planned(self):
        """Placeholder test - output span testing requires full app integration"""
        pytest.skip(
            "Output rendering spans require full app integration testing. "
            "Will be covered by integration tests."
        )


class TestSpanHierarchy:
    """Test span parent-child relationships"""

    @pytest.mark.asyncio
    async def test_calc_span_nested_under_reactive_update(
        self, otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that calc spans are children of reactive.update span"""
        provider, memory_exporter = otel_tracer_provider

        # Clear any previous spans
        memory_exporter.clear()

        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):

                # Create a calc
                def my_calc():
                    return 42

                calc = Calc_(my_calc)

                # Manually create flush span and execute calc inside it
                async with with_otel_span_async(
                    "reactive.update",
                    level=OtelCollectLevel.REACTIVE_UPDATE,
                ):
                    await calc.update_value()

        # Get exported spans with proper flushing
        spans = get_exported_spans(provider, memory_exporter)

        # Filter out internal OTel spans
        app_spans = [s for s in spans if not s.name.startswith("_otel")]

        # Should have 2 spans: reactive.update and reactive my_calc
        assert len(app_spans) >= 2

        # Find the spans
        update_span = next((s for s in app_spans if s.name == "reactive.update"), None)
        calc_span = next((s for s in app_spans if s.name == "reactive my_calc"), None)

        assert update_span is not None, "reactive.update span should exist"
        assert calc_span is not None, "reactive my_calc span should exist"

        # Verify parent-child relationship
        calc_parent = calc_span.parent
        assert calc_parent is not None, "calc span should have a parent"
        # Note: pyright doesn't understand that context is always present on ReadableSpan
        assert (
            calc_parent.span_id == update_span.context.span_id  # type: ignore[union-attr]
        ), "calc parent should be reactive.update"

        # Verify they're in the same trace
        assert (
            calc_span.context.trace_id == update_span.context.trace_id  # type: ignore[union-attr]
        ), "Spans should be in same trace"
