# OpenTelemetry Integration for Shiny

This guide covers everything you need to know about using OpenTelemetry with Shiny for Python.

## Quick Start Example

For a working demonstration of OpenTelemetry with Shiny, see the [open-telemetry example](../../examples/open-telemetry/) which shows:
- Console exporter setup
- Collection level control with `@otel_collect`
- Reactive value logging
- Side-by-side comparison of full vs. suppressed telemetry

## Table of Contents

1. [What is OpenTelemetry?](#what-is-opentelemetry)
2. [Why Use OpenTelemetry with Shiny?](#why-use-opentelemetry-with-shiny)
3. [Getting Started](#getting-started)
4. [Collection Levels](#collection-levels)
5. [Configuration](#configuration)
6. [Programmatic Control](#programmatic-control)
7. [Best Practices](#best-practices)
8. [Observability Backends](#observability-backends)
9. [Troubleshooting](#troubleshooting)

## What is OpenTelemetry?

[OpenTelemetry](https://opentelemetry.io/) is an open-source observability framework that provides a standardized way to collect telemetry data (traces, metrics, and logs) from applications. It's vendor-neutral and widely supported by observability platforms.

**Key concepts:**

- **Traces**: Records of requests flowing through your application, showing timing and dependencies
- **Spans**: Individual units of work within a trace (e.g., a function execution)
- **Logs**: Structured log events with context
- **Attributes**: Key-value metadata attached to spans and logs

## Why Use OpenTelemetry with Shiny?

Shiny applications have complex reactive execution flows that can be difficult to debug and optimize. OpenTelemetry provides:

### 1. **Reactive Flow Visualization**

See exactly how reactive computations propagate through your app:
- Which calcs and effects execute during each update cycle
- Parent-child relationships between reactive components
- Execution timing and ordering

### 2. **Performance Analysis**

Identify bottlenecks in your application:
- Which outputs take the longest to render
- Which reactive computations are slow
- How many reactive invalidations occur per user interaction

### 3. **Debugging Aid**

Understand unexpected behavior:
- Why certain reactive computations run (or don't run)
- Execution order when multiple things invalidate
- Async operation context propagation

### 4. **Production Monitoring**

Track application health in production:
- Session lifecycle and user behavior patterns
- Error rates and types
- Performance over time

## Getting Started

### Installation

Install Shiny with OpenTelemetry support:

```bash
pip install "shiny[otel]"
```

This installs both the OpenTelemetry API (required) and SDK (for exporters).

### Basic Setup

Configure OpenTelemetry before running your app:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from shiny import App, ui, render, reactive

# Configure OpenTelemetry
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

# Your app code...
```

**Note**: Shiny uses lazy initialization for its OpenTelemetry tracer, so you can configure it anywhere in your code before the app runs.

### Quick Example

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from shiny import App, ui, render, reactive

# Configure OTel
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

app_ui = ui.page_fluid(
    ui.input_slider("n", "N", 1, 100, 50),
    ui.output_text("result"),
)

def server(input, output, session):
    @render.text
    def result():
        return f"Value: {input.n()}"

app = App(app_ui, server)
```

Run with:
```bash
export SHINY_OTEL_COLLECT=all
python app.py
```

You'll see OpenTelemetry spans printed to the console showing Shiny's internal execution.

## Collection Levels

Shiny provides five collection levels to control the granularity of telemetry:

### `none` (0)
No Shiny telemetry collected. Use when you want to completely disable Shiny's instrumentation while keeping your own custom spans.

**Overhead**: None
**Use case**: Disabling telemetry entirely

### `session` (1)
Only session lifecycle spans (session start/end, HTTP/WebSocket connections).

**Overhead**: Minimal (1-2 spans per session)
**Use case**: Basic session tracking in production

### `reactive_update` (2)
Session spans + reactive update cycle spans (one span per flush cycle).

**Overhead**: Low (1 span per reactive flush)
**Use case**: Understanding how many update cycles occur

### `reactivity` (3)
Everything from `reactive_update` + individual reactive execution spans (calcs, effects, outputs) + value update logs.

**Overhead**: Moderate (1 span per reactive computation)
**Use case**: Detailed debugging and development

### `all` (4)
All available telemetry (currently equivalent to `reactivity`). Reserved for future expansion.

**Overhead**: Moderate
**Use case**: Maximum observability

### Setting Collection Level

Via environment variable:
```bash
export SHINY_OTEL_COLLECT=session  # or: none, reactive_update, reactivity, all
python app.py
```

The default level is `all` if not specified.

## Configuration

### Environment Variables

#### `SHINY_OTEL_COLLECT`

Sets the default collection level for the application.

```bash
# Minimal overhead - session lifecycle only
export SHINY_OTEL_COLLECT=session

# Balanced - update cycles tracked
export SHINY_OTEL_COLLECT=reactive_update

# Full detail - all reactive executions
export SHINY_OTEL_COLLECT=reactivity

# Maximum (same as reactivity currently)
export SHINY_OTEL_COLLECT=all
```

### OpenTelemetry SDK Configuration

The OpenTelemetry SDK itself supports many configuration options via environment variables:

```bash
# Service name
export OTEL_SERVICE_NAME=my-shiny-app

# OTLP exporter endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Resource attributes
export OTEL_RESOURCE_ATTRIBUTES=deployment.environment=production,service.version=1.0.0

# Trace sampling
export OTEL_TRACES_SAMPLER=parentbased_traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1  # Sample 10% of traces
```

See [OpenTelemetry SDK Configuration](https://opentelemetry.io/docs/languages/sdk-configuration/) for full details.

## Programmatic Control

**Important**: The collection level for a reactive object (calc, effect, output) is
captured at **initialization time** -- when the reactive object is created -- not
when the reactive function executes. This means `otel_collect` affects which level
is stored on the reactive object during its definition, and that level is used for
all subsequent executions.

### Decorator

Use `otel_collect` as a decorator to set the collection level for a reactive function.
The decorator stamps the collection level on the function, and the reactive object
reads it when it is created:

```python
from shiny.otel import otel_collect

@reactive.calc
@otel_collect("none")
def sensitive_computation():
    """This entire calc runs without Shiny telemetry on every execution."""
    api_key = input.api_key()
    return validate_api_key(api_key)
```

**Important**: When decorating reactive objects, apply `otel_collect` **before** (i.e., closer to the function than) the reactive decorator:

```python
# Correct order -- otel_collect is applied to the function first,
# then @reactive.calc reads the stamped level at initialization time
@reactive.calc
@otel_collect("none")
def my_calc():
    pass

# Incorrect - will raise TypeError
@otel_collect("none")  # Cannot wrap a reactive object
@reactive.calc
def my_calc():
    pass
```

### Context Manager (Initialization Time Only)

Use `otel_collect` as a context manager to set the collection level during
**reactive object creation**. Any reactive objects defined inside the `with` block
will capture that level at initialization time:

```python
from shiny.otel import otel_collect

with otel_collect("none"):
    # Reactive objects created inside this block capture "none" as their level
    @reactive.calc
    def sensitive_calc():
        """Telemetry is disabled for this calc (level captured at init)."""
        return load_secrets()

# Reactive objects created outside the block use the default level
@reactive.calc
def normal_calc():
    """Telemetry uses the default level."""
    return load_public_data()
```

**Does NOT work at runtime**: Using `with otel_collect(...)` inside a reactive
function body has no effect on Shiny's internal telemetry for that reactive object,
because the collection level was already captured when the object was created:

```python
@reactive.calc
def my_calc():
    # THIS DOES NOT WORK as intended for Shiny telemetry.
    # The calc's collection level was already set at initialization time.
    with otel_collect("none"):
        # Shiny's span for this calc was already started with
        # the level captured at init, so this block cannot suppress it.
        sensitive_data = load_secrets()
    return sensitive_data
```

### Nested Context Managers (Initialization Time)

Context managers can be nested during initialization, with the innermost taking precedence:

```python
from shiny.otel import otel_collect

with otel_collect("session"):
    # Reactive objects created here capture "session" level

    with otel_collect("none"):
        # Reactive objects created here capture "none" level
        @reactive.calc
        def no_telemetry_calc():
            return "no spans"

    # Back to "session" level for objects created here
    @reactive.calc
    def session_only_calc():
        return "session spans only"
```

## Best Practices

### 1. Use Batch Processor in Production

Replace `SimpleSpanProcessor` with `BatchSpanProcessor` for better performance:

```python
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Instead of:
# provider.add_span_processor(SimpleSpanProcessor(exporter))

# Use:
provider.add_span_processor(BatchSpanProcessor(exporter))
```

Batching reduces overhead by buffering spans and sending them in batches.

### 2. Choose Appropriate Collection Level

Development:
```bash
export SHINY_OTEL_COLLECT=reactivity  # Full detail for debugging
```

Production:
```bash
export SHINY_OTEL_COLLECT=session  # Minimal overhead
# or
export SHINY_OTEL_COLLECT=reactive_update  # Balanced
```

### 3. Add Resource Attributes

Include service metadata in your traces:

```python
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "my-shiny-app",
    "service.version": "1.2.3",
    "deployment.environment": "production",
    "service.namespace": "analytics-team",
})

provider = TracerProvider(resource=resource)
```

### 4. Protect Sensitive Data

Use `otel_collect("none")` for operations involving sensitive data:

```python
from shiny.otel import otel_collect

@reactive.calc
@otel_collect("none")
def process_credentials():
    """Disable telemetry for credential handling."""
    username = input.username()
    password = input.password()
    return authenticate(username, password)
```

**Remember**: `otel_collect` only disables **Shiny's internal telemetry**. Your own custom OpenTelemetry spans are unaffected.

### 5. Enable Error Sanitization

When `app.sanitize_errors=True`, Shiny automatically sanitizes error messages in spans to prevent leaking sensitive information:

```python
app = App(app_ui, server, sanitize_errors=True)
```

### 6. Use Sampling in High-Traffic Apps

For high-traffic applications, use trace sampling to reduce overhead:

```python
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

# Sample 10% of traces
sampler = ParentBasedTraceIdRatio(0.1)
provider = TracerProvider(sampler=sampler)
```

### 7. Add Custom Spans for Business Logic

Complement Shiny's spans with your own for business-critical operations:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@reactive.calc
def expensive_computation():
    with tracer.start_as_current_span("database_query") as span:
        span.set_attribute("query.type", "analytics")
        result = run_query()
        span.set_attribute("query.rows", len(result))
        return result
```

## Observability Backends

Shiny's OpenTelemetry integration works with any OTLP-compatible backend.

### Jaeger (Open Source)

Perfect for local development and self-hosted monitoring.

**Setup**:
```bash
docker run -d --name jaeger \
    -p 16686:16686 \
    -p 4317:4317 \
    jaegertracing/all-in-one:latest
```

**Configuration**:
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from shiny import App, ui, render, reactive

# Configure OpenTelemetry
resource = Resource.create({
    "service.name": "my-shiny-app",
    "deployment.environment": "development",
})
provider = TracerProvider(resource=resource)

# Use OTLP exporter to send traces to Jaeger
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",  # Jaeger's OTLP gRPC port
    insecure=True,  # For local development
)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)

# Now build your Shiny app
app_ui = ui.page_fluid(
    ui.h2("My Shiny App"),
    ui.input_slider("n", "N", 1, 100, 50),
    ui.output_text("result"),
)

def server(input, output, session):
    @render.text
    def result():
        import time
        time.sleep(0.1)  # Simulate work
        return f"Value: {input.n()}"

app = App(app_ui, server)
```

**UI**: http://localhost:16686

Open the Jaeger UI to explore your Shiny app's traces. You'll see:
- Session lifecycle spans
- Reactive update cycles
- Individual calc/effect/output executions
- Timing and nesting relationships

### Pydantic Logfire (Managed)

Modern observability platform with excellent Python support.

**Setup**:
```bash
pip install logfire
```

**Configuration**:
```python
import logfire

# Configure BEFORE importing Shiny
logfire.configure(
    token=os.environ["LOGFIRE_TOKEN"],
    service_name="my-shiny-app",
)

# Now import Shiny
from shiny import App, ui
```

**UI**: https://logfire.pydantic.dev

### Honeycomb (Managed)

Powerful observability platform focused on trace analysis.

**Configuration**:
```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

exporter = OTLPSpanExporter(
    endpoint="https://api.honeycomb.io/v1/traces",
    headers={"x-honeycomb-team": os.environ["HONEYCOMB_API_KEY"]},
)
```

### Datadog (Managed)

Enterprise observability platform with APM features.

**Configuration**:
```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

exporter = OTLPSpanExporter(
    endpoint="https://http-intake.logs.datadoghq.com/v1/traces",
    headers={
        "DD-API-KEY": os.environ["DD_API_KEY"],
    },
)
```

### New Relic (Managed)

Full-stack observability platform.

**Configuration**:
```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

exporter = OTLPSpanExporter(
    endpoint="https://otlp.nr-data.net:4317",
    headers={"api-key": os.environ["NEW_RELIC_LICENSE_KEY"]},
)
```

### Console (Development)

Simple console output for debugging. See the [open-telemetry example](../../examples/open-telemetry/) for a complete working demonstration of console exporters with collection control.

```python
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

exporter = ConsoleSpanExporter()
```

## Troubleshooting

### No Spans Appearing

**Problem**: Console/backend shows no spans from Shiny.

**Solutions**:
1. Verify OpenTelemetry is configured correctly

2. Check collection level:
   ```bash
   # Make sure it's not "none"
   export SHINY_OTEL_COLLECT=all
   ```

3. Verify exporter endpoint is correct and reachable

4. Check for error messages in console

### Too Much Overhead

**Problem**: Application performance degraded with OpenTelemetry enabled.

**Solutions**:
1. Use `BatchSpanProcessor` instead of `SimpleSpanProcessor`:
   ```python
   from opentelemetry.sdk.trace.export import BatchSpanProcessor
   provider.add_span_processor(BatchSpanProcessor(exporter))
   ```

2. Lower collection level:
   ```bash
   export SHINY_OTEL_COLLECT=session  # Minimal
   ```

3. Enable sampling:
   ```python
   from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio
   provider = TracerProvider(sampler=ParentBasedTraceIdRatio(0.1))
   ```

4. Use `otel_collect("none")` for high-frequency operations:
   ```python
   @reactive.calc
   @otel_collect("none")
   def high_frequency_calc():
       pass
   ```

### Sensitive Data in Traces

**Problem**: Passwords or API keys appearing in span attributes.

**Solutions**:
1. Use `@otel_collect("none")` decorator on sensitive reactive functions:
   ```python
   @reactive.calc
   @otel_collect("none")
   def process_api_keys():
       api_key = input.api_key()
       return validate(api_key)
   ```

2. Use `with otel_collect("none"):` when defining reactive objects that handle sensitive data
   (the level is captured at initialization time):
   ```python
   with otel_collect("none"):
       @reactive.calc
       def handle_password():
           password = input.password()
           return hash_password(password)
   ```

3. Enable error sanitization:
   ```python
   app = App(app_ui, server, sanitize_errors=True)
   ```

### Spans Not Nested Correctly

**Problem**: Parent-child relationships incorrect in traces.

**Solutions**:
1. Ensure you're using async context propagation correctly
2. Check that custom spans use `start_as_current_span()`:
   ```python
   # CORRECT
   with tracer.start_as_current_span("my_span"):
       pass

   # WRONG - breaks context chain
   span = tracer.start_span("my_span")
   ```

### Backend Not Receiving Traces

**Problem**: OpenTelemetry configured but backend shows no data.

**Solutions**:
1. Check exporter endpoint URL and authentication
2. Verify network connectivity to backend
3. Check backend-specific requirements (headers, format)
4. Use `ConsoleSpanExporter` first to verify spans are generated:
   ```python
   from opentelemetry.sdk.trace.export import ConsoleSpanExporter
   provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
   ```

### ImportError: No module named 'opentelemetry'

**Problem**: OpenTelemetry not installed.

**Solution**:
```bash
pip install "shiny[otel]"
```

## Next Steps

- **Examples**: Check out `_dev/otel/examples/` for working example apps
- **API Reference**: See API documentation for `shiny.otel` module
- **OpenTelemetry Docs**: https://opentelemetry.io/docs/languages/python/
- **Shiny Docs**: https://shiny.posit.co/py/

## Getting Help

- **GitHub Issues**: https://github.com/posit-dev/py-shiny/issues
- **Community**: https://forum.posit.co/c/shiny
- **OpenTelemetry Community**: https://cloud-native.slack.com (#otel-python channel)
