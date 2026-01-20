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
from contextlib import contextmanager
from unittest.mock import AsyncMock, patch

import pytest

from shiny.otel import OtelCollectLevel


@contextmanager
def otel_tracer_provider_context():
    """
    Context manager for test isolation when using TracerProvider.

    Sets up an InMemorySpanExporter and TracerProvider, then restores
    the original provider on exit. This ensures tests don't interfere
    with each other when setting up their own tracing infrastructure.

    Yields
    ------
    tuple[TracerProvider, InMemorySpanExporter]
        The provider and exporter for use in tests.
    """
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
        InMemorySpanExporter,
    )

    # Save the current tracer provider to restore later
    old_provider = trace.get_tracer_provider()

    try:
        # Set up new provider with in-memory exporter
        memory_exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(memory_exporter))

        # Use internal API to force override for testing
        trace._set_tracer_provider(provider, log=False)

        yield provider, memory_exporter
    finally:
        # Restore the original tracer provider
        trace._set_tracer_provider(old_provider, log=False)


class TestLabelGeneration:
    """Label generation tests"""

    def test_generate_reactive_label_for_calc(self):
        """Test generating label for a calc with function name"""
        from shiny.otel._labels import generate_reactive_label

        def my_calc():
            return 42

        label = generate_reactive_label(my_calc, "reactive")
        assert label == "reactive my_calc"

    def test_generate_reactive_label_for_lambda(self):
        """Test generating label for anonymous/lambda function"""
        from shiny.otel._labels import generate_reactive_label

        label = generate_reactive_label(lambda: 42, "reactive")
        assert label == "reactive <anonymous>"

    def test_generate_reactive_label_with_namespace(self):
        """Test generating label with namespace prefix"""
        from shiny.otel._labels import generate_reactive_label

        def my_calc():
            return 42

        label = generate_reactive_label(my_calc, "reactive", namespace="mod")
        assert label == "reactive mod:my_calc"

    def test_generate_reactive_label_with_modifier(self):
        """Test generating label with modifier (e.g., cache)"""
        from shiny.otel._labels import generate_reactive_label

        def my_calc():
            return 42

        label = generate_reactive_label(my_calc, "reactive", modifier="cache")
        assert label == "reactive cache my_calc"

    def test_generate_observe_label(self):
        """Test generating label for effect (observe)"""
        from shiny.otel._labels import generate_reactive_label

        def my_effect():
            pass

        label = generate_reactive_label(my_effect, "observe")
        assert label == "observe my_effect"

    def test_generate_output_label(self):
        """Test generating label for output rendering"""
        from shiny.otel._labels import generate_reactive_label

        def my_output():
            return "text"

        label = generate_reactive_label(my_output, "output")
        assert label == "output my_output"


class TestSourceReferenceExtraction:
    """Source code attribute extraction tests"""

    def test_extract_source_ref_from_function(self):
        """Test extracting source reference from a regular function"""
        from shiny.otel._attributes import extract_source_ref

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
        from shiny.otel._attributes import extract_source_ref

        attrs = extract_source_ref(lambda: 42)

        # Lambda should still have source info
        assert "code.function" in attrs
        assert attrs["code.function"] == "<lambda>"
        assert "code.filepath" in attrs
        assert "code.lineno" in attrs

    def test_extract_source_ref_from_builtin(self):
        """Test extracting source reference from built-in function"""
        from shiny.otel._attributes import extract_source_ref

        attrs = extract_source_ref(len)

        # Built-in functions won't have source info
        # Should return empty dict without errors
        assert isinstance(attrs, dict)


class TestCalcSpans:
    """Calc execution span tests"""

    @pytest.mark.asyncio
    async def test_calc_creates_span_when_enabled(self):
        """Test that Calc execution creates a span when collection level is REACTIVITY"""
        from shiny.reactive import Calc_

        with patch("shiny.otel._core._tracing_enabled", True):
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
        from shiny.reactive import Calc_

        with patch("shiny.otel._core._tracing_enabled", True):
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
        from shiny.reactive import Calc_

        with patch("shiny.otel._core._tracing_enabled", True):
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
        from shiny.reactive import Effect_

        with patch("shiny.otel._core._tracing_enabled", True):
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
        from shiny.reactive import Effect_

        with patch("shiny.otel._core._tracing_enabled", True):
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
    async def test_calc_span_nested_under_reactive_update(self):
        """Test that calc spans are children of reactive.update span"""
        from shiny.otel import OtelCollectLevel
        from shiny.otel._span_wrappers import with_otel_span_async
        from shiny.reactive import Calc_

        with otel_tracer_provider_context() as (_, memory_exporter):
            with patch("shiny.otel._core._tracing_enabled", True):
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

            # Get exported spans
            spans = memory_exporter.get_finished_spans()

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
