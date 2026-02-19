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

3. Control collect level via environment variable:
   ```bash
   export SHINY_OTEL_COLLECT=all  # or: none, session, reactive_update, reactivity
   python app.py
   ```

## Collect Levels

Control what Shiny internal telemetry is collected:

- **none**: No Shiny telemetry collected
- **session**: Session lifecycle spans only
- **reactive_update**: Session + reactive update cycles
- **reactivity**: Session + reactive cycles + individual reactive executions + value logs
- **all**: All available Shiny telemetry (currently equivalent to reactivity)

**Important**: These levels only affect Shiny's internal spans and logs. Any OpenTelemetry
spans you create manually in your application code are unaffected.

## Programmatic Control

Use the `otel_collect` context manager to control Shiny's collect level dynamically:

```python
from shiny import App, ui, reactive
from shiny.otel import otel_collect

@reactive.calc
def my_calc():
    with otel_collect("none"):
        # No Shiny telemetry for sensitive operations
        # (your own spans are still recorded)
        sensitive_data = load_secrets()

    # Normal Shiny telemetry resumes here
    return process_data(sensitive_data)
```

## API Reference

Main export:
- `otel_collect`: Context manager/decorator to temporarily change Shiny's collect level
"""

from __future__ import annotations

from ._collect import get_otel_collect_level
from ._core import get_otel_logger, get_otel_tracer
from ._decorators import otel_collect

__all__ = (
    # Collect level management
    "get_otel_collect_level",
    # Core functionality
    "get_otel_tracer",
    "get_otel_logger",
    # User-facing API
    "otel_collect",
)
