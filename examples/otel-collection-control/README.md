# OpenTelemetry Collection Control Example

This example demonstrates how to control Shiny's OpenTelemetry collection levels using the `shiny.otel.otel_collect` context manager and decorator.

## Overview

The `otel_collect` function allows you to dynamically control which **Shiny internal telemetry** is collected. This is useful for:

- **Privacy**: Suppress Shiny telemetry for sensitive operations
- **Performance**: Reduce overhead by disabling Shiny telemetry for specific code paths
- **Debugging**: Enable detailed Shiny telemetry only for specific areas
- **Compliance**: Ensure sensitive data isn't inadvertently sent to telemetry backends

**Important**: `otel_collect` only affects Shiny's internal spans and logs (session lifecycle, reactive execution, value updates, etc.). Any OpenTelemetry spans you create manually in your application code are unaffected and will continue to be recorded normally.

### Timing

Collection levels are captured when reactive objects (`reactive.value`, `reactive.calc`, `reactive.effect`) are **created**, not when they are executed. This means the level used for Shiny's internal spans (reactive execution, value updates) is **permanently set** at object creation time:

```python
# Collection level is captured when reactive.calc() creates the Calc object
with otel_collect("none"):
    @reactive.calc
    def my_calc():
        return expensive_computation()

# Later execution of my_calc() ALWAYS uses "none" for Shiny's internal spans,
# regardless of what the current otel_collect level is
```

Using `otel_collect` inside a reactive function body will **not** affect Shiny's internal spans for that reactive - the level was already captured at object creation. To dynamically control collection levels, use the decorator on render functions, which are created at app initialization:

```python
# Incorrect - this does NOT change Shiny's internal span level for my_calc
@reactive.calc
def my_calc():
    with otel_collect("none" if is_sensitive() else "all"):
        return expensive_computation()  # Shiny still uses level from creation time

# Correct - use decorator on render functions to suppress telemetry
@render.text
@otel_collect("none")
def result_private():
    # Entire render function runs without Shiny telemetry
    return compute_private_data()

@render.text  # Uses default "all" level
def result_public():
    # Shiny telemetry enabled for this render
    return compute_public_data()
```

**Note**: Using `otel_collect` inside a reactive function body *will* affect any manual spans you create with `shiny_otel_span()`, just not Shiny's automatic internal spans.

## Features Demonstrated

### 1. Context Manager Usage

```python
from shiny.otel import otel_collect

with otel_collect("none"):
    # No Shiny telemetry collected in this block
    # (your own spans are still recorded)
    sensitive_result = process_sensitive_data()
```

### 2. Decorator Usage

```python
from shiny.otel import otel_collect

@render.text
@otel_collect("none")
def result_private():
    # Entire function runs without Shiny telemetry
    # (your own spans are still recorded)
    return compute_private_data()
```

### 3. Nested Collection Levels

```python
from shiny.otel import otel_collect

@render.text
def result_mixed():
    # Outer function has normal telemetry
    public_data = fetch_public_data()

    # Suppress telemetry for sensitive processing
    with otel_collect("none"):
        sensitive_result = process_sensitive_data()

    # Back to normal telemetry
    return f"Public: {public_data}, Result: {sensitive_result}"
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

Install the OpenTelemetry SDK:

```bash
pip install opentelemetry-sdk
```

### Run the App

```bash
python app.py
```

The app will open in your browser. As you interact with the buttons:

- **"Compute (Normal Telemetry)"**: Creates spans for reactive execution
- **"Compute (No Telemetry)"**: Suppresses all telemetry using `@otel_collect("none")`

Watch the console output to see which spans are created.

## Environment Variable Configuration

You can set the default collection level via environment variable:

```bash
export SHINY_OTEL_COLLECT=session
python app.py
```

The `otel_collect` context manager and decorator will override this default.

## Key Concepts

### Default Collection Level

The default collection level is set by:

1. The `SHINY_OTEL_COLLECT` environment variable (defaults to `all`)
2. Can be overridden programmatically with `otel_collect()`

### Span Hierarchy

When telemetry is enabled (`all` level), you'll see spans like:

```text
session.start
  └─ reactive_update
      ├─ reactive.calc result
      ├─ reactive.effect <lambda>
      └─ output result_private (suppressed with @otel_collect("none"))
```

### Privacy Considerations

Use `otel_collect("none")` to wrap code that:

- Processes passwords, API keys, or other secrets
- Handles personally identifiable information (PII)
- Performs operations that shouldn't be visible in external monitoring systems

## Real-World Use Cases

### 1. Protecting Sensitive Computations

```python
from shiny.otel import otel_collect

@reactive.calc
def user_data():
    with otel_collect("none"):
        # Don't send PII to telemetry backend
        user_info = fetch_user_from_database()
        decrypt_sensitive_fields(user_info)
    return user_info
```

### 2. Performance-Critical Paths

```python
from shiny.otel import otel_collect

@otel_collect("none")
def fast_update():
    # Disable telemetry overhead for high-frequency updates
    for i in range(10000):
        counter.set(counter.get() + 1)
```

### 3. Conditional Telemetry

```python
from shiny.otel import otel_collect

def process_data():
    level = "none" if is_production() else "all"
    with otel_collect(level):
        # Detailed telemetry in dev, none in production
        result = expensive_computation()
    return result
```

## Additional Resources

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [Shiny OpenTelemetry Guide](../../docs/otel.md) (if available)
- [py-shiny GitHub Repository](https://github.com/posit-dev/py-shiny)

## Related Examples

- `otel-basic/`: Basic OpenTelemetry setup
- `otel-value-logging/`: Value update logging with source references
- `otel-jaeger/`: Integration with Jaeger backend (if available)
