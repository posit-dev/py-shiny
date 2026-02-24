"""
Comprehensive async reactivity test app with OpenTelemetry instrumentation.

Tests async patterns:
- Async render functions with concurrent operations
- Async calcs that spawn background tasks
- Async effects with asyncio tasks
- Context propagation through await boundaries
"""

import asyncio
from typing import List

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

# Set up OpenTelemetry with console exporter for verification
provider = TracerProvider()
processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)


async def async_computation(value: str, delay: float) -> str:
    """Simulates async work that takes time."""
    await asyncio.sleep(delay)
    return f"Processed: {value}"


async def spawn_background_tasks(values: List[str]) -> List[str]:
    """Spawns multiple concurrent async tasks."""
    tasks = [asyncio.create_task(async_computation(val, 0.01)) for val in values]
    results = await asyncio.gather(*tasks)
    return list(results)


app_ui = ui.page_fluid(
    ui.h2("Async Reactivity with OTel Test App"),
    ui.input_text("text_input", "Enter text", value="test"),
    ui.input_action_button("trigger_calc", "Trigger Calc"),
    ui.input_action_button("trigger_effect", "Trigger Effect"),
    ui.output_code("async_render_output"),
    ui.output_code("calc_output"),
    ui.output_code("effect_output"),
    ui.output_code("background_tasks_output"),
)


def server(input: Inputs, output: Outputs, session: Session):
    effect_counter = reactive.value(0)

    @render.code
    async def async_render_output():
        """Async render that awaits multiple operations."""
        # This should create a reactive span that contains await operations
        text = input.text_input()
        result1 = await async_computation(text, 0.01)
        result2 = await async_computation(result1, 0.01)
        return f"Render result: {result2}"

    @reactive.calc
    # Wait for trigger
    @reactive.event(input.trigger_calc)
    async def async_calc():
        """Async calc that spawns background tasks."""
        text = input.text_input()
        # Spawn concurrent tasks
        results = await spawn_background_tasks([text, text + "_2", text + "_3"])
        return ", ".join(results)

    @render.code
    async def calc_output():
        """Display calc result."""
        result = await async_calc()
        return f"Calc result: {result}"

    @reactive.effect
    @reactive.event(input.trigger_effect)
    async def async_effect():
        """Async effect that does background work."""
        # This should create an effect span containing async operations
        text = input.text_input()
        await async_computation(text, 0.01)

        # Update reactive value
        effect_counter.set(effect_counter() + 1)

    @render.code
    def effect_output():
        """Display effect counter."""
        return f"Effect executed: {effect_counter()} times"

    @render.code
    async def background_tasks_output():
        """Render that uses gather to run tasks in parallel."""
        text = input.text_input()

        # Run multiple independent async operations in parallel
        async def task1():
            await asyncio.sleep(0.01)
            return f"Task1: {text}"

        async def task2():
            await asyncio.sleep(0.01)
            return f"Task2: {text}"

        async def task3():
            await asyncio.sleep(0.01)
            return f"Task3: {text}"

        results = await asyncio.gather(task1(), task2(), task3())
        return " | ".join(results)


app = App(app_ui, server)
