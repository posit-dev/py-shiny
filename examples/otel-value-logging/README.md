## OpenTelemetry Value Logging

<a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fotel-value-logging%2Fapp.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' align="right" /></a>

This example demonstrates automatic logging of reactive value updates using OpenTelemetry. When the collection level is set to `reactivity` or higher, py-shiny automatically emits log events whenever reactive values are updated.

### Features Demonstrated

- **Automatic Value Logging**: See log events when input values change
- **Session Context**: Logs include session IDs for traceability
- **Namespace Support**: Module-scoped values include namespace prefixes
- **Custom Reactive Values**: Track updates to user-defined reactive values
- **Collection Level Control**: Enable/disable logging via environment variable

### Running the Example

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set the collection level to enable value logging:
   ```bash
   export SHINY_OTEL_COLLECT=reactivity
   ```

3. Run the app:
   ```bash
   shiny run app.py
   ```

### What to Look For

Interact with the app and watch the console output for log events:

- **Move the slider** → logs `"Set reactiveVal slider"` with session ID
- **Type in the text input** → logs `"Set reactiveVal text"` with session ID
- **Click the increment button** → logs `"Set reactiveVal <unnamed>"` with session ID
  - The counter variable is named `counter` in the code, but appears as `<unnamed>` in logs because Python doesn't support introspecting variable names for standalone `reactive.Value()` objects. Only input values (which are stored in a dictionary) can have their names automatically captured.

Each log event includes:

- **Body**: The log message (e.g., `"Set reactiveVal slider"`)
- **Severity**: `DEBUG` level
- **Attributes**: `session.id` for traceability across requests
- **Timestamp**: When the value was updated

The console output will show both OpenTelemetry spans (for reactive execution) and log events (for value updates), giving you complete observability into your application's reactive behavior.

### OpenTelemetry Setup

The example includes a complete OpenTelemetry setup with:
- **TracerProvider**: For distributed tracing (spans)
- **LoggerProvider**: For structured logging (log events)
- **Console Exporters**: Output directly to console for easy viewing

In production, you would typically export to backends like Jaeger, Zipkin, or cloud observability platforms.

### Collection Levels

- `none`: No telemetry collected
- `session`: Session lifecycle only
- `reactive_update`: Session + reactive flush cycles
- **`reactivity`**: Session + reactive flush + value updates (required for this example)
- `all`: All available telemetry

### Learn More

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [py-shiny OpenTelemetry Integration](../../shiny/otel/)
