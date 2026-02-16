"""
OpenTelemetry instrumentation for Shiny applications.

This module provides OpenTelemetry tracing and logging support for Shiny applications,
allowing you to observe application behavior, performance, and reactive execution flow.

## Quick Start

To enable OpenTelemetry tracing in your Shiny application:

1. Install the OpenTelemetry SDK:
   ```bash
   pip install opentelemetry-sdk
   ```

2. Configure the SDK before importing shiny:
   ```python
   from opentelemetry import trace
   from opentelemetry.sdk.trace import TracerProvider
   from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

   # Set up the tracer provider
   provider = TracerProvider()
   provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
   trace.set_tracer_provider(provider)

   # Now import and use shiny
   from shiny import App, ui

   app = App(...)
   ```

3. Control collection level via environment variable:
   ```bash
   export SHINY_OTEL_COLLECT=all  # or: none, session, reactive_update, reactivity
   python app.py
   ```

## Collection Levels

- **none**: No telemetry collected
- **session**: Session lifecycle spans only
- **reactive_update**: Session + reactive flush cycles
- **reactivity**: Session + reactive flush + individual reactive computations
- **all**: All available telemetry (currently equivalent to reactivity)

## Programmatic Control

Use the `otel_collect` context manager to control collection dynamically:

```python
from shiny import App, ui, reactive
from shiny.otel import otel_collect

@reactive.calc
def my_calc():
    with otel_collect("none"):
        # No telemetry for sensitive operations
        sensitive_data = load_secrets()

    # Normal telemetry resumes here
    return process_data(sensitive_data)
```

## API Reference

Main exports:
- `OtelCollectLevel`: Enum defining collection levels
- `should_otel_collect`: Check if telemetry should be collected for a given level
- `otel_collect`: Context manager to temporarily change collection level (Phase 7)
"""

from __future__ import annotations

from ._collect import OtelCollectLevel, get_otel_collect_level, should_otel_collect
from ._core import (
    get_otel_logger,
    get_otel_tracer,
    is_otel_tracing_enabled,
)

__all__ = (
    # Collection level management
    "OtelCollectLevel",
    "get_otel_collect_level",
    "should_otel_collect",
    # Core functionality
    "get_otel_tracer",
    "get_otel_logger",
    "is_otel_tracing_enabled",
    # User-facing API (will be added in Phase 7)
    # "otel_collect",
)
