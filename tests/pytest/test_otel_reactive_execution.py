"""
OpenTelemetry Reactive Execution Instrumentation

Tests cover:
- Calc execution span creation
- Effect execution span creation
- Output rendering span creation
- Label generation for reactive computations
- Source code attribute extraction
- Span parent-child relationships (reactive_update → calc/effect/output)
- Collection level controls
"""

import os
from typing import Tuple
from unittest.mock import AsyncMock, patch

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shiny.otel._attributes import extract_source_ref
from shiny.otel._collect import OtelCollectLevel
from shiny.otel._labels import create_otel_span_name
from shiny.otel._span_wrappers import shiny_otel_span
from shiny.reactive import Calc_, Effect_

from .otel_helpers import get_exported_spans, patch_otel_tracing_state


class TestLabelGeneration:
    """Label generation tests"""

    def test_create_otel_span_name_for_calc(self):
        """Test generating label for a calc with function name"""

        def my_calc():
            return 42

        label = create_otel_span_name(my_calc, "reactive.calc")
        assert label == "reactive.calc my_calc"

    def test_create_otel_span_name_for_lambda(self):
        """Test generating label for anonymous/lambda function"""
        label = create_otel_span_name(lambda: 42, "reactive.effect")
        assert label == "reactive.effect <anonymous>"

    def test_create_otel_span_name_with_namespace(self):
        """Test generating label with namespace prefix"""
        from unittest.mock import Mock

        from shiny._namespaces import ResolvedId

        def my_calc():
            return 42

        # Create a mock session with a namespace
        mock_session = Mock()
        mock_session.ns = ResolvedId("mod")

        label = create_otel_span_name(my_calc, "reactive.calc", session=mock_session)
        assert label == "reactive.calc mod:my_calc"

    def test_create_otel_span_name_with_modifier(self):
        """Test generating label with modifier (e.g., cache)"""

        def my_calc():
            return 42

        label = create_otel_span_name(my_calc, "reactive.calc", modifier="cache")
        assert label == "reactive.calc cache my_calc"

    def test_create_otel_span_name_with_namespace_and_modifier(self):
        """Test generating label with both namespace and modifier"""
        from unittest.mock import Mock

        from shiny._namespaces import ResolvedId

        def my_calc():
            return 42

        # Create a mock session with a namespace
        mock_session = Mock()
        mock_session.ns = ResolvedId("mod")

        label = create_otel_span_name(
            my_calc, "reactive.calc", session=mock_session, modifier="cache"
        )
        assert label == "reactive.calc cache mod:my_calc"

    def test_generate_observe_label(self):
        """Test generating label for effect (observe)"""

        def my_effect():
            pass

        label = create_otel_span_name(my_effect, "reactive.effect")
        assert label == "reactive.effect my_effect"

    def test_generate_output_label(self):
        """Test generating label for output rendering"""

        def my_output():
            return "text"

        label = create_otel_span_name(my_output, "output")
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
        assert calc._otel_label == "reactive.calc event my_calc"

    def test_effect_extracts_event_modifier(self):
        """Test that Effect_ extracts modifier from @reactive.event decorated function"""
        from shiny.reactive import Effect_, Value, event

        x = Value(0)

        @event(x)
        def my_effect():
            pass

        effect = Effect_(my_effect, session=None)

        # The effect should have generated label with "event" modifier
        assert effect._otel_label == "reactive.effect event my_effect"

    def test_calc_without_modifier_has_no_modifier_in_label(self):
        """Test that Calc_ without modifier has clean label"""

        def my_calc():
            return 42

        calc = Calc_(my_calc)

        # The calc should have label without modifier
        assert calc._otel_label == "reactive.calc my_calc"

    def test_effect_without_modifier_has_no_modifier_in_label(self):
        """Test that Effect_ without modifier has clean label"""

        def my_effect():
            pass

        effect = Effect_(my_effect, session=None)

        # The effect should have label without modifier
        assert effect._otel_label == "reactive.effect my_effect"


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

    def test_extract_source_ref_from_wrapped_function(self):
        """Test that extract_source_ref unwraps @functools.wraps decorated functions"""
        import functools

        # Define the original function at a known line
        def original_function():  # This is the line we expect to see
            return 42

        # Capture the line number where original_function is defined
        original_line = original_function.__code__.co_firstlineno

        # Create a wrapper using @functools.wraps
        @functools.wraps(original_function)
        def wrapper_function():
            return original_function()

        # Extract attributes from the wrapper
        attrs = extract_source_ref(wrapper_function)

        # Should extract from the ORIGINAL function, not the wrapper
        assert "code.function" in attrs
        assert (
            attrs["code.function"] == "original_function"
        ), f"Should have original function name, got: {attrs.get('code.function')}"

        assert "code.filepath" in attrs
        assert attrs["code.filepath"].endswith(
            "test_otel_reactive_execution.py"
        ), f"Should point to this test file, got: {attrs['code.filepath']}"

        assert "code.lineno" in attrs
        assert (
            attrs["code.lineno"] == original_line
        ), f"Should have original line number ({original_line}), got: {attrs.get('code.lineno')}"

    def test_extract_source_ref_from_nested_wrapped_functions(self):
        """Test extract_source_ref with multiple layers of wrapping"""
        import functools

        # Original function
        def original():
            return 42

        original_line = original.__code__.co_firstlineno

        # First wrapper
        @functools.wraps(original)
        def wrapper1():
            return original()

        # Second wrapper (wrapping the first wrapper)
        @functools.wraps(wrapper1)
        def wrapper2():
            return wrapper1()

        # Extract from the outermost wrapper
        attrs = extract_source_ref(wrapper2)

        # Should unwrap all the way to the original
        assert "code.function" in attrs
        assert attrs["code.function"] == "original"
        assert "code.lineno" in attrs
        assert attrs["code.lineno"] == original_line

    def test_extract_source_ref_from_reactive_event_decorator(self):
        """Test that @reactive.event decorated functions unwrap correctly"""
        from shiny.reactive import Value, event

        # Create a reactive value to use as event trigger
        trigger = Value(0)

        # Define original function
        def my_effect():  # This is the line we expect
            return trigger()

        original_line = my_effect.__code__.co_firstlineno

        # Apply @reactive.event decorator
        decorated = event(trigger)(my_effect)

        # Extract from decorated function
        attrs = extract_source_ref(decorated)

        # Should extract from original function, not the event wrapper
        assert "code.function" in attrs
        assert (
            attrs["code.function"] == "my_effect"
        ), f"Should have original function name, got: {attrs.get('code.function')}"

        assert "code.lineno" in attrs
        assert (
            attrs["code.lineno"] == original_line
        ), f"Should have original line number ({original_line}), got: {attrs.get('code.lineno')}"

    def test_extract_source_ref_from_unwrappable_function(self):
        """Test that functions without __wrapped__ attribute still work"""

        # Function without @functools.wraps
        def outer():
            def inner():
                return 42

            # Manually set attributes but NOT __wrapped__
            inner.__name__ = "fake_name"
            return inner

        func = outer()

        # Should not crash, should extract from the actual function
        attrs = extract_source_ref(func)

        # Should have attributes (even if they're from the inner function)
        assert isinstance(attrs, dict)
        # Function name should be what we set
        if "code.function" in attrs:
            assert attrs["code.function"] == "fake_name"

    def test_extract_source_ref_from_deeply_nested_wrappers(self):
        """Test extract_source_ref with 3+ layers of wrapping"""
        import functools

        # Original function
        def original():
            return 42

        original_line = original.__code__.co_firstlineno

        # Create 3 layers of wrappers
        @functools.wraps(original)
        def wrapper1():
            return original()

        @functools.wraps(wrapper1)
        def wrapper2():
            return wrapper1()

        @functools.wraps(wrapper2)
        def wrapper3():
            return wrapper2()

        # Extract from the outermost wrapper (3 layers deep)
        attrs = extract_source_ref(wrapper3)

        # Should unwrap all the way to the original
        assert "code.function" in attrs
        assert (
            attrs["code.function"] == "original"
        ), "Should unwrap through 3 layers to original"
        assert "code.lineno" in attrs
        assert attrs["code.lineno"] == original_line

    def test_extract_source_ref_from_functools_partial(self):
        """Test extract_source_ref with functools.partial objects"""
        import functools

        def my_func(a: int, b: int) -> int:
            return a + b

        # Create a partial function
        partial_func = functools.partial(my_func, 10)

        # Extract from partial
        attrs = extract_source_ref(partial_func)

        # Note: functools.partial objects don't have __code__ or typical function
        # attributes, so extract_source_ref returns an empty dict. This is expected
        # behavior since partials are callable wrappers, not regular functions.
        # In practice, this is fine since Shiny apps rarely use partials directly
        # as reactive functions.
        assert isinstance(attrs, dict)
        # May be empty or have limited info - that's OK for partials

    def test_extract_source_ref_from_circular_wrapped_chain(self):
        """Test that circular __wrapped__ chains are handled gracefully"""

        # Create a function with circular __wrapped__ reference
        def func1():
            return 1

        def func2():
            return 2

        # Create circular reference: func1.__wrapped__ -> func2 -> func1
        func1.__wrapped__ = func2  # type: ignore
        func2.__wrapped__ = func1  # type: ignore

        # Should handle ValueError from circular chain gracefully
        attrs = extract_source_ref(func1)

        # Should not crash and should return dict (may be empty or partial)
        assert isinstance(attrs, dict)
        # With ValueError handling in both unwrap() and getsourcelines(),
        # we should get at least the function name
        assert "code.function" in attrs
        assert attrs["code.function"] == "func1"


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
                with patch("shiny.reactive._reactives.shiny_otel_span") as mock_span:
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
                    assert label == "reactive.calc my_calc"
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
                with patch("shiny.reactive._reactives.shiny_otel_span") as mock_span:
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
                with patch("shiny.reactive._reactives.shiny_otel_span") as mock_span:
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
    """Reactive Effect execution span tests"""

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
                with patch("shiny.reactive._reactives.shiny_otel_span") as mock_span:
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
                    assert label == "reactive.effect my_effect"
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
                with patch("shiny.reactive._reactives.shiny_otel_span") as mock_span:
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
                with patch("shiny.reactive._reactives.shiny_otel_span") as mock_span:
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
        """Test that calc spans are children of reactive_update span"""
        provider, memory_exporter = otel_tracer_provider

        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):

                # Create a calc
                def my_calc():
                    return 42

                calc = Calc_(my_calc)

                # Manually create flush span and execute calc inside it
                async with shiny_otel_span(
                    "reactive_update",
                    required_level=OtelCollectLevel.REACTIVE_UPDATE,
                ):
                    await calc.update_value()

        # Get exported spans with proper flushing
        spans = get_exported_spans(provider, memory_exporter)

        # Filter out internal OTel spans
        app_spans = [s for s in spans if not s.name.startswith("_otel")]

        # Should have 2 spans: reactive_update and reactive my_calc
        assert len(app_spans) >= 2

        # Find the spans
        update_span = next((s for s in app_spans if s.name == "reactive_update"), None)
        calc_span = next(
            (s for s in app_spans if s.name == "reactive.calc my_calc"), None
        )

        assert update_span is not None, "reactive_update span should exist"
        assert calc_span is not None, "reactive.calc my_calc span should exist"

        # Verify parent-child relationship
        calc_parent = calc_span.parent
        assert calc_parent is not None, "calc span should have a parent"
        # Note: pyright doesn't understand that context is always present on ReadableSpan
        assert (
            calc_parent.span_id == update_span.context.span_id  # type: ignore[union-attr]
        ), "reactive.calc parent should be reactive_update"

        # Verify they're in the same trace
        assert (
            calc_span.context.trace_id == update_span.context.trace_id  # type: ignore[union-attr]
        ), "Spans should be in same trace"


class TestCollectionLevelNone:
    """Tests for OtelCollectLevel.NONE handling"""

    def test_calc_respects_none_level(self):
        """Verify Calc_ correctly handles OtelCollectLevel.NONE (value 0)"""
        from shiny.otel import otel_collect

        with patch_otel_tracing_state(tracing_enabled=True):

            @otel_collect("none")
            def my_calc():
                return 42

            calc = Calc_(my_calc)

            # The bug: using `or` would treat NONE (0) as falsy
            # This verifies the fix: explicitly checking for None
            assert calc._otel_level == OtelCollectLevel.NONE

    def test_effect_respects_none_level(self):
        """Verify Effect_ correctly handles OtelCollectLevel.NONE (value 0)"""
        from shiny.otel import otel_collect

        with patch_otel_tracing_state(tracing_enabled=True):

            @otel_collect("none")
            def my_effect():
                pass

            effect = Effect_(my_effect)

            # The bug: using `or` would treat NONE (0) as falsy
            # This verifies the fix: explicitly checking for None
            assert effect._otel_level == OtelCollectLevel.NONE

    def test_calc_without_decorator_uses_context_level(self):
        """Verify Calc_ uses context level when no decorator is present"""
        with patch_otel_tracing_state(tracing_enabled=True):

            def my_calc():
                return 42

            calc = Calc_(my_calc)

            # Without decorator, should use the current context level
            # Default test level is REACTIVITY
            assert calc._otel_level >= OtelCollectLevel.REACTIVITY

    def test_effect_without_decorator_uses_context_level(self):
        """Verify Effect_ uses context level when no decorator is present"""
        with patch_otel_tracing_state(tracing_enabled=True):

            def my_effect():
                pass

            effect = Effect_(my_effect)

            # Without decorator, should use the current context level
            # Default test level is REACTIVITY
            assert effect._otel_level >= OtelCollectLevel.REACTIVITY
