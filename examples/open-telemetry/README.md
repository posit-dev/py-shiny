# OpenTelemetry Example

This example demonstrates OpenTelemetry integration with Shiny, including:
- Console exporter setup for viewing traces
- Collection level control with `@otel.suppress`
- Reactive value logging
- Side-by-side comparison of normal vs. suppressed telemetry

For comprehensive documentation, please see the [Shiny OpenTelemetry documentation](https://shiny.posit.co/py/api/core/OpenTelemetry.html).

## Overview

The `otel.suppress` API allows you to dynamically control which **Shiny internal telemetry** is collected. This is useful for:

- **Privacy**: Suppress Shiny telemetry for sensitive operations
- **Performance**: Reduce overhead by disabling Shiny telemetry for specific code paths
- **Debugging**: Enable detailed Shiny telemetry only for specific areas
- **Compliance**: Ensure sensitive data isn't inadvertently sent to telemetry backends

**Important**: `otel.suppress` only affects Shiny's internal spans and logs (session lifecycle, reactive execution, value updates, etc.). Any OpenTelemetry spans you create manually in your application code are unaffected and will continue to be recorded normally.

`otel.collect` is the counterpart — it re-enables Shiny's internal telemetry for specific
reactive objects, even when initialized inside a broad `otel.suppress()` block.

### Timing

The suppression setting is captured when reactive objects (`reactive.value`, `reactive.calc`, `reactive.effect`) are **created**, not when they are executed. This means the setting used for Shiny's internal spans (reactive execution, value updates) is **permanently set** at object creation time:

```python
from shiny import otel

# Suppression is captured when reactive.calc() creates the Calc object
with otel.suppress():
    @reactive.calc
    def my_calc():
        return expensive_computation()

# Later execution of my_calc() ALWAYS has telemetry suppressed,
# regardless of the current context
```

Using `otel.suppress()` inside a reactive function body will **not** affect Shiny's internal spans for that reactive - the setting was already captured at object creation. To suppress telemetry, use the decorator on render functions, which are created at app initialization:

```python
from shiny import otel

# Incorrect - this does NOT change Shiny's internal span level for my_calc
@reactive.calc
def my_calc():
    with otel.suppress():
        return expensive_computation()  # Shiny still uses level from creation time

# Correct - use decorator on render functions to suppress telemetry
@render.text
@otel.suppress
def result_private():
    # Entire render function runs without Shiny telemetry
    return compute_private_data()

@render.text  # Uses default "all" level
def result_public():
    # Shiny telemetry enabled for this render
    return compute_public_data()
```

**Note**: Using `otel.suppress()` inside a reactive function body *will* affect any manual spans you create with `shiny_otel_span()`, just not Shiny's automatic internal spans.

## Features Demonstrated

### 1. Context Manager Usage

```python
from shiny import otel

with otel.suppress():
    # No Shiny telemetry collected in this block
    # (your own spans are still recorded)
    sensitive_result = process_sensitive_data()
```

### 2. Decorator Usage

```python
from shiny import otel

@render.text
@otel.suppress
def result_private():
    # Entire function runs without Shiny telemetry
    # (your own spans are still recorded)
    return compute_private_data()
```

### 3. Nested Suppression

```python
from shiny import otel

with otel.suppress():
    # No Shiny telemetry in this block
    @render.text
    def result_private():
        # Entire function runs without Shiny telemetry
        # (your own spans are still recorded)
        return compute_private_data()

# Back to default telemetry level
```

### 4. `otel.collect` Usage

Re-enable telemetry inside a suppressed block:

```python
from shiny import otel

with otel.suppress():
    # Most reactive objects here have telemetry suppressed

    with otel.collect():
        @reactive.calc
        def public_calc():
            # Telemetry enabled despite the outer suppress
            return load_public_data()
```

## Collection Levels

The following collection levels control **Shiny's internal telemetry** (from least to most detailed):

- **`none`**: No Shiny telemetry collected
- **`session`**: Session lifecycle spans only
- **`reactive_update`**: Session + reactive update cycles
- **`reactivity`**: Session + reactive cycles + individual reactive executions + value updates
- **`all`**: All available Shiny telemetry (currently equivalent to `reactivity`)

**Note**: Your own manually created spans are always recorded regardless of these settings.

## Running the Example

### Prerequisites

Install Shiny with OpenTelemetry support:

```bash
pip install shiny[otel]
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

### Run the App

```bash
python app.py
```

The app will open in your browser. As you interact with the buttons:

- **"Compute (Normal Telemetry)"**: Creates Shiny spans for reactive execution
- **"Compute (No Telemetry)"**: Suppresses all telemetry using `@otel.suppress`

Watch the console output to see which spans are created.

## Environment Variable Configuration

You can set the default collection level via environment variable:

```bash
export SHINY_OTEL_COLLECT=session
python app.py
```

The `otel.suppress` decorator and context manager will override this default.

## Key Concepts

### Default Collection Level

The default collection level is set by:

1. The `SHINY_OTEL_COLLECT` environment variable (defaults to `all`)
2. Can be overridden programmatically with `otel.suppress` / `otel.suppress()`

### Span Hierarchy

When telemetry is enabled (`all` level), you'll see spans like:

```text
session.start
  └─ reactive_update
      ├─ reactive.calc result
      ├─ reactive.effect <lambda>
      └─ output result_private (suppressed with @otel.suppress)
```

### Privacy Considerations

Use `otel.suppress` to wrap code that:

- Processes passwords, API keys, or other secrets
- Handles personally identifiable information (PII)
- Performs operations that shouldn't be visible in external monitoring systems

## Additional Resources

- [Shiny OpenTelemetry Documentation](https://shiny.posit.co/py/api/core/OpenTelemetry.html) - Complete guide with examples
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [py-shiny GitHub Repository](https://github.com/posit-dev/py-shiny)
