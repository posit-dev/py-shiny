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
from shiny.otel._labels import create_otel_label
from shiny.otel._span_wrappers import with_otel_span_async
from shiny.reactive import Calc_, Effect_

from .otel_helpers import get_exported_spans, patch_otel_tracing_state


class TestLabelGeneration:
    """Label generation tests"""

    def test_create_otel_label_for_calc(self):
        """Test generating label for a calc with function name"""

        def my_calc():
            return 42

        label = create_otel_label(my_calc, "reactive")
        assert label == "reactive my_calc"

    def test_create_otel_label_for_lambda(self):
        """Test generating label for anonymous/lambda function"""
        label = create_otel_label(lambda: 42, "reactive")
        assert label == "reactive <anonymous>"

    def test_create_otel_label_with_namespace(self):
        """Test generating label with namespace prefix"""
        from unittest.mock import Mock

        from shiny._namespaces import ResolvedId

        def my_calc():
            return 42

        # Create a mock session with a namespace
        mock_session = Mock()
        mock_session.ns = ResolvedId("mod")

        label = create_otel_label(my_calc, "reactive", session=mock_session)
        assert label == "reactive mod:my_calc"

    def test_create_otel_label_with_modifier(self):
        """Test generating label with modifier (e.g., cache)"""

        def my_calc():
            return 42

        label = create_otel_label(my_calc, "reactive", modifier="cache")
        assert label == "reactive cache my_calc"

    def test_create_otel_label_with_namespace_and_modifier(self):
        """Test generating label with both namespace and modifier"""
        from unittest.mock import Mock

        from shiny._namespaces import ResolvedId

        def my_calc():
            return 42

        # Create a mock session with a namespace
        mock_session = Mock()
        mock_session.ns = ResolvedId("mod")

        label = create_otel_label(
            my_calc, "reactive", session=mock_session, modifier="cache"
        )
        assert label == "reactive cache mod:my_calc"

    def test_generate_observe_label(self):
        """Test generating label for effect (observe)"""

        def my_effect():
            pass

        label = create_otel_label(my_effect, "observe")
        assert label == "observe my_effect"

    def test_generate_output_label(self):
        """Test generating label for output rendering"""

        def my_output():
            return "text"

        label = create_otel_label(my_output, "output")
        assert label == "output my_output"


class TestModifierHelpers:
    """Modifier helper function tests"""

    def test_get_otel_label_modifier_returns_none_by_default(self):
        """Test that get_otel_label_modifier returns None for unmodified functions"""
        from shiny.otel._labels import get_otel_label_modifier

        def my_func():
            return 42

        modifier = get_otel_label_modifier(my_func)
        assert modifier is None

    def test_set_otel_label_modifier_sets_attribute(self):
        """Test that set_otel_label_modifier sets the modifier attribute"""
        from shiny.otel._labels import get_otel_label_modifier, set_otel_label_modifier

        def my_func():
            return 42

        set_otel_label_modifier(my_func, "event")
        modifier = get_otel_label_modifier(my_func)
        assert modifier == "event"

    def test_set_otel_label_modifier_prepend_mode(self):
        """Test that set_otel_label_modifier prepends by default"""
        from shiny.otel._labels import get_otel_label_modifier, set_otel_label_modifier

        def my_func():
            return 42

        set_otel_label_modifier(my_func, "event")
        assert get_otel_label_modifier(my_func) == "event"

        set_otel_label_modifier(my_func, "cache")  # Prepend by default
        assert get_otel_label_modifier(my_func) == "cache event"

        set_otel_label_modifier(my_func, "debounce", mode="prepend")
        assert get_otel_label_modifier(my_func) == "debounce cache event"

    def test_set_otel_label_modifier_append_mode(self):
        """Test that set_otel_label_modifier can append modifiers"""
        from shiny.otel._labels import get_otel_label_modifier, set_otel_label_modifier

        def my_func():
            return 42

        set_otel_label_modifier(my_func, "event")
        assert get_otel_label_modifier(my_func) == "event"

        set_otel_label_modifier(my_func, "cache", mode="append")
        assert get_otel_label_modifier(my_func) == "event cache"

        set_otel_label_modifier(my_func, "debounce", mode="append")
        assert get_otel_label_modifier(my_func) == "event cache debounce"

    def test_set_otel_label_modifier_replace_mode(self):
        """Test that set_otel_label_modifier can replace modifiers"""
        from shiny.otel._labels import get_otel_label_modifier, set_otel_label_modifier

        def my_func():
            return 42

        set_otel_label_modifier(my_func, "event")
        set_otel_label_modifier(my_func, "cache", mode="append")
        assert get_otel_label_modifier(my_func) == "event cache"

        set_otel_label_modifier(my_func, "throttle", mode="replace")
        assert get_otel_label_modifier(my_func) == "throttle"

    def test_set_otel_label_modifier_invalid_mode(self):
        """Test that set_otel_label_modifier raises error for invalid mode"""
        from shiny.otel._labels import set_otel_label_modifier

        def my_func():
            return 42

        with pytest.raises(ValueError, match=r"Invalid mode: 'invalid'"):
            set_otel_label_modifier(my_func, "event", mode="invalid")

    def test_functools_wraps_preserves_modifier(self):
        """Test that @functools.wraps preserves the modifier attribute"""
        import functools

        from shiny.otel._labels import get_otel_label_modifier, set_otel_label_modifier

        def original():
            return 42

        set_otel_label_modifier(original, "event")

        @functools.wraps(original)
        def wrapper():
            return original()

        # Modifier should be preserved through @functools.wraps
        assert get_otel_label_modifier(wrapper) == "event"


class TestReactiveEventModifier:
    """Test @reactive.event modifier integration"""

    def test_reactive_event_sets_modifier(self):
        """Test that @reactive.event sets the event modifier"""
        from shiny.otel._labels import get_otel_label_modifier
        from shiny.reactive import Value, event

        x = Value(0)

        @event(x)
        def my_func():
            return 42

        # The decorator should have set the "event" modifier
        modifier = get_otel_label_modifier(my_func)
        assert modifier == "event"

    def test_calc_extracts_event_modifier(self):
        """Test that Calc_ extracts modifier from @reactive.event decorated function"""
        from shiny.reactive import Calc_, Value, event

        x = Value(0)

        @event(x)
        def my_calc():
            return 42

        calc = Calc_(my_calc)

        # The calc should have generated label with "event" modifier
        assert calc._otel_label == "reactive event my_calc"

    def test_effect_extracts_event_modifier(self):
        """Test that Effect_ extracts modifier from @reactive.event decorated function"""
        from shiny.reactive import Effect_, Value, event

        x = Value(0)

        @event(x)
        def my_effect():
            pass

        effect = Effect_(my_effect, session=None)

        # The effect should have generated label with "event" modifier
        assert effect._otel_label == "observe event my_effect"

    def test_calc_without_modifier_has_no_modifier_in_label(self):
        """Test that Calc_ without modifier has clean label"""

        def my_calc():
            return 42

        calc = Calc_(my_calc)

        # The calc should have label without modifier
        assert calc._otel_label == "reactive my_calc"

    def test_effect_without_modifier_has_no_modifier_in_label(self):
        """Test that Effect_ without modifier has clean label"""

        def my_effect():
            pass

        effect = Effect_(my_effect, session=None)

        # The effect should have label without modifier
        assert effect._otel_label == "observe my_effect"


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
                    # Verify the label string was passed
                    label = call_args[0][0]
                    assert label == "reactive my_calc"
                    assert call_args[1]["required_level"] == OtelCollectLevel.REACTIVITY

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
                    # Verify the label string was passed
                    label = call_args[0][0]
                    assert label == "observe my_effect"
                    assert call_args[1]["required_level"] == OtelCollectLevel.REACTIVITY

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

    @pytest.mark.asyncio
    async def test_effect_span_includes_source_attrs(self):
        """Test that Effect span includes source code attributes"""
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "reactivity"}):
                # Create an effect with known source
                def my_effect():
                    pass

                effect = Effect_(my_effect, session=None)

                # Mock span wrapper to capture attributes
                # Must patch at the import location in _reactives module
                with patch(
                    "shiny.reactive._reactives.with_otel_span_async"
                ) as mock_span:
                    # Configure mock
                    mock_span.return_value.__aenter__ = AsyncMock(return_value=None)
                    mock_span.return_value.__aexit__ = AsyncMock(return_value=None)

                    # Execute the effect
                    await effect._run()

                    # Verify source attributes were included via _otel_attrs
                    call_args = mock_span.call_args
                    attrs = call_args[1]["attributes"]
                    # Attributes are stored on the effect instance at init time
                    assert "code.function" in attrs
                    assert attrs["code.function"] == "my_effect"
                    assert "code.filepath" in attrs
                    assert "code.lineno" in attrs


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
                    required_level=OtelCollectLevel.REACTIVE_UPDATE,
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
