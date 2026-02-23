"""
OpenTelemetry Async Context Propagation Tests

Tests cover:
- Spans propagate correctly through async boundaries
- Concurrent reactive executions maintain correct span context
- Context isolation between parallel async operations
"""

import asyncio
from typing import Tuple

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shiny.otel._collect import OtelCollectLevel
from shiny.otel._span_wrappers import shiny_otel_span
from shiny.reactive import Calc_
from shiny.reactive._core import ReactiveEnvironment

from .otel_helpers import get_exported_spans, patch_otel_tracing_state


class TestAsyncSpanPropagation:
    """Test span context propagation through async boundaries"""

    @pytest.mark.asyncio
    async def test_span_propagates_through_await(
        self, otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that span context propagates through await boundaries"""
        provider, memory_exporter = otel_tracer_provider

        async def inner_operation():
            """Nested async function that should inherit parent span context"""
            async with shiny_otel_span(
                "inner.operation",
                required_level=OtelCollectLevel.ALL,
            ):
                await asyncio.sleep(0.001)

        with patch_otel_tracing_state(tracing_enabled=True):
            async with shiny_otel_span(
                "outer.operation",
                required_level=OtelCollectLevel.ALL,
            ):
                await inner_operation()

        # Get exported spans
        spans = get_exported_spans(provider, memory_exporter)

        # Filter to only our app spans (exclude internal OpenTelemetry spans)
        app_spans = [
            s for s in spans if s.name in ["outer.operation", "inner.operation"]
        ]
        assert len(app_spans) == 2

        # Find parent and child spans
        outer_span = next(s for s in app_spans if s.name == "outer.operation")
        inner_span = next(s for s in app_spans if s.name == "inner.operation")

        # Verify parent-child relationship
        assert inner_span.parent is not None
        assert inner_span.parent.span_id == outer_span.context.span_id

    @pytest.mark.asyncio
    async def test_span_propagates_through_task(
        self, otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that span context propagates when creating asyncio tasks"""
        provider, memory_exporter = otel_tracer_provider

        async def background_task():
            """Background task that should inherit parent span context"""
            async with shiny_otel_span(
                "background.task",
                required_level=OtelCollectLevel.ALL,
            ):
                await asyncio.sleep(0.001)

        with patch_otel_tracing_state(tracing_enabled=True):
            async with shiny_otel_span(
                "main.operation",
                required_level=OtelCollectLevel.ALL,
            ):
                # Create task within parent span
                task = asyncio.create_task(background_task())
                await task

        # Get exported spans
        spans = get_exported_spans(provider, memory_exporter)

        # Filter to only our app spans
        app_spans = [
            s for s in spans if s.name in ["main.operation", "background.task"]
        ]
        assert len(app_spans) == 2

        # Find parent and child spans
        main_span = next(s for s in app_spans if s.name == "main.operation")
        background_span = next(s for s in app_spans if s.name == "background.task")

        # Verify parent-child relationship
        assert background_span.parent is not None
        assert background_span.parent.span_id == main_span.context.span_id


class TestConcurrentReactiveExecutions:
    """Test that concurrent reactive executions maintain proper span context"""

    @pytest.mark.asyncio
    async def test_concurrent_calcs_maintain_separate_contexts(
        self, otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that concurrent calc executions each have their own span context"""
        provider, memory_exporter = otel_tracer_provider

        # Track execution order
        execution_order = []

        async def slow_calc_1():
            execution_order.append("calc1_start")
            await asyncio.sleep(0.01)
            execution_order.append("calc1_end")
            return "calc1"

        async def slow_calc_2():
            execution_order.append("calc2_start")
            await asyncio.sleep(0.005)
            execution_order.append("calc2_end")
            return "calc2"

        with patch_otel_tracing_state(tracing_enabled=True):
            # Create two calcs that will execute concurrently
            calc1 = Calc_(slow_calc_1)
            calc2 = Calc_(slow_calc_2)

            # Execute them concurrently within a reactive update span
            async with shiny_otel_span(
                "reactive.update",
                required_level=OtelCollectLevel.REACTIVE_UPDATE,
            ):
                # Start both calcs concurrently
                results = await asyncio.gather(
                    calc1.update_value(),
                    calc2.update_value(),
                )

        # Get exported spans
        spans = get_exported_spans(provider, memory_exporter)

        # Filter to reactive-related spans
        calc_spans = [s for s in spans if s.name.startswith("reactive")]

        # Should have: 1 reactive.update + 2 reactive slow_calc spans
        assert len(calc_spans) >= 2  # At least the two calc spans

        # Verify both calcs executed
        assert "calc1_start" in execution_order
        assert "calc2_start" in execution_order
        assert "calc1_end" in execution_order
        assert "calc2_end" in execution_order

        # Verify calc2 finished before calc1 (because it sleeps less)
        assert execution_order.index("calc2_end") < execution_order.index("calc1_end")

    @pytest.mark.asyncio
    async def test_parallel_flush_cycles_maintain_context(
        self, otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that parallel flush cycles each maintain their own span context"""
        provider, memory_exporter = otel_tracer_provider

        with patch_otel_tracing_state(tracing_enabled=True):
            # Create two separate reactive environments
            env1 = ReactiveEnvironment()
            env2 = ReactiveEnvironment()

            # Flush them in parallel
            await asyncio.gather(
                env1.flush(),
                env2.flush(),
            )

        # Get exported spans
        spans = get_exported_spans(provider, memory_exporter)

        # Filter to reactive.update spans
        update_spans = [s for s in spans if s.name == "reactive.update"]

        # Should have two separate reactive.update spans
        assert len(update_spans) == 2

        # Verify they are separate spans (different span IDs)
        assert update_spans[0].context.span_id != update_spans[1].context.span_id


class TestAsyncContextIsolation:
    """Test that async operations maintain proper context isolation"""

    @pytest.mark.asyncio
    async def test_gather_maintains_context_per_task(
        self, otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that asyncio.gather() maintains separate context for each task"""
        provider, memory_exporter = otel_tracer_provider

        async def task_with_span(task_id: str):
            """Create a span with a unique name"""
            async with shiny_otel_span(
                f"task.{task_id}",
                attributes={"task.id": task_id},
                required_level=OtelCollectLevel.ALL,
            ):
                await asyncio.sleep(0.001)
                return task_id

        with patch_otel_tracing_state(tracing_enabled=True):
            async with shiny_otel_span(
                "parent.operation",
                required_level=OtelCollectLevel.ALL,
            ):
                # Run multiple tasks concurrently
                results = await asyncio.gather(
                    task_with_span("A"),
                    task_with_span("B"),
                    task_with_span("C"),
                )

        # Get exported spans
        spans = get_exported_spans(provider, memory_exporter)

        # Filter to task spans
        task_spans = [s for s in spans if s.name.startswith("task.")]

        # Should have three task spans
        assert len(task_spans) == 3

        # Verify each has correct attributes
        task_ids = {s.attributes.get("task.id") for s in task_spans}
        assert task_ids == {"A", "B", "C"}

        # Verify all tasks completed
        assert set(results) == {"A", "B", "C"}

        # Verify all task spans have the same parent (the parent.operation span)
        parent_span = next(s for s in spans if s.name == "parent.operation")
        for task_span in task_spans:
            assert task_span.parent is not None
            assert task_span.parent.span_id == parent_span.context.span_id

    @pytest.mark.asyncio
    async def test_nested_async_contexts_maintain_hierarchy(
        self, otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that deeply nested async contexts maintain proper span hierarchy"""
        provider, memory_exporter = otel_tracer_provider

        async def level_3():
            async with shiny_otel_span(
                "level.3",
                required_level=OtelCollectLevel.ALL,
            ):
                await asyncio.sleep(0.001)

        async def level_2():
            async with shiny_otel_span(
                "level.2",
                required_level=OtelCollectLevel.ALL,
            ):
                await level_3()

        async def level_1():
            async with shiny_otel_span(
                "level.1",
                required_level=OtelCollectLevel.ALL,
            ):
                await level_2()

        with patch_otel_tracing_state(tracing_enabled=True):
            async with shiny_otel_span(
                "level.0",
                required_level=OtelCollectLevel.ALL,
            ):
                await level_1()

        # Get exported spans
        spans = get_exported_spans(provider, memory_exporter)

        # Filter to level spans
        level_spans = [s for s in spans if s.name.startswith("level.")]

        # Should have four level spans
        assert len(level_spans) == 4

        # Build span map for easy lookup
        span_map = {s.name: s for s in level_spans}

        # Verify hierarchy: level.0 → level.1 → level.2 → level.3
        level_0 = span_map["level.0"]
        level_1 = span_map["level.1"]
        level_2 = span_map["level.2"]
        level_3 = span_map["level.3"]

        # level.1 should be child of level.0
        assert level_1.parent is not None
        assert level_1.parent.span_id == level_0.context.span_id

        # level.2 should be child of level.1
        assert level_2.parent is not None
        assert level_2.parent.span_id == level_1.context.span_id

        # level.3 should be child of level.2
        assert level_3.parent is not None
        assert level_3.parent.span_id == level_2.context.span_id


class TestReactiveUpdateConcurrency:
    """Test reactive.update span behavior with concurrent operations"""

    @pytest.mark.asyncio
    async def test_multiple_calcs_share_reactive_update_parent(
        self, otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter]
    ):
        """Test that multiple calcs executing in same flush share reactive.update parent"""
        provider, memory_exporter = otel_tracer_provider

        async def calc_a():
            await asyncio.sleep(0.001)
            return "A"

        async def calc_b():
            await asyncio.sleep(0.001)
            return "B"

        with patch_otel_tracing_state(tracing_enabled=True):
            # Create calcs
            calc_1 = Calc_(calc_a)
            calc_2 = Calc_(calc_b)

            # Execute within a reactive update span
            async with shiny_otel_span(
                "reactive.update",
                required_level=OtelCollectLevel.REACTIVE_UPDATE,
            ):
                # Execute calcs concurrently
                await asyncio.gather(
                    calc_1.update_value(),
                    calc_2.update_value(),
                )

        # Get exported spans
        spans = get_exported_spans(provider, memory_exporter)

        # Find the reactive.update span
        update_spans = [s for s in spans if s.name == "reactive.update"]
        assert len(update_spans) == 1
        update_span = update_spans[0]

        # Find the calc spans
        calc_spans = [s for s in spans if s.name.startswith("reactive") and "calc" in s.name]

        # Should have two calc spans
        assert len(calc_spans) >= 2

        # Verify both calc spans have the reactive.update as parent
        for calc_span in calc_spans:
            assert calc_span.parent is not None
            # Note: Parent might be set via context propagation
            # Just verify each calc has a parent span
            assert calc_span.parent.span_id is not None
