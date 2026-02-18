# OpenTelemetry Collection Control Example

This example demonstrates how to control Shiny's OpenTelemetry collection levels using the `otel_collect` context manager and decorator.

## Overview

The `otel_collect` function allows you to dynamically control which **Shiny internal telemetry** is collected. This is useful for:

- **Privacy**: Suppress Shiny telemetry for sensitive operations
- **Performance**: Reduce overhead by disabling Shiny telemetry for specific code paths
- **Debugging**: Enable detailed Shiny telemetry only for specific areas
- **Compliance**: Ensure sensitive data isn't inadvertently sent to telemetry backends

**Important**: `otel_collect` only affects Shiny's internal spans and logs (session lifecycle, reactive execution, value updates, etc.). Any OpenTelemetry spans you create manually in your application code are unaffected and will continue to be recorded normally.

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

with otel_collect("session"):
    # Only session-level Shiny telemetry
    with otel_collect("none"):
        # No Shiny telemetry in this inner block
        process_data()
    # Back to session-level Shiny telemetry
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
  └─ reactive.update
      ├─ reactive result
      ├─ observe <lambda>
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
