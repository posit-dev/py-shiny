---
name: otel
description: Use when adding observability to a Shiny for Python (py-shiny) app with OpenTelemetry - tracing reactive execution, profiling slow outputs or update cycles, monitoring sessions in production, exporting spans to a backend (Jaeger, Logfire, Honeycomb, Datadog, OTLP), suppressing telemetry for sensitive code, or when tempted to call trace.set_tracer_provider() inside app code to set up instrumentation.
---

# OpenTelemetry for Shiny for Python apps

## Overview

Shiny has built-in OpenTelemetry instrumentation: it emits spans for session
lifecycle, reactive update cycles, and individual calc/effect/output executions.
Enable it with **zero-code auto-instrumentation** — launch the app under
`opentelemetry-instrument`. Do NOT configure providers inside app code
(`trace.set_tracer_provider(...)`): providers install once per process, so
in-code setup is silently ignored under external instrumentation.

## Setup and run

```bash
uv pip install "shiny[otel]"   # includes opentelemetry-distro[otlp]
```

Print spans to the console while developing:

```bash
opentelemetry-instrument --traces_exporter console --logs_exporter console \
    --metrics_exporter none shiny run app.py
```

Export to a backend (OTLP to `http://localhost:4317` is the default; any
OTLP-compatible backend works — Jaeger, Logfire, Honeycomb, Datadog, ...):

```bash
OTEL_SERVICE_NAME=my-shiny-app opentelemetry-instrument shiny run app.py
```

All standard `OTEL_*` environment variables apply (`OTEL_EXPORTER_OTLP_ENDPOINT`,
`OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_EXPORTER_OTLP_PROTOCOL`, sampling via
`OTEL_TRACES_SAMPLER`). `--reload` is compatible. The app needs no OTel code at
all. Shiny resolves the tracer provider lazily at span-creation time, so the
wrapper's provider is picked up automatically.

At the `all` level the span hierarchy looks like:

```text
session_start
  └─ reactive_update
      ├─ reactive.calc filtered_data
      └─ output result
```

## Collection levels: `SHINY_OTEL_COLLECT`

Controls how much Shiny telemetry is emitted (default `all`):

| Level | Emits | Use |
|---|---|---|
| `none` | nothing from Shiny | disable Shiny spans, keep your own |
| `session` | session lifecycle only | low-overhead production |
| `reactive_update` | + one span per flush cycle | balanced production |
| `reactivity` | + per calc/effect/output spans, value-update logs | development, debugging |
| `all` | everything (currently = `reactivity`) | maximum detail |

```bash
SHINY_OTEL_COLLECT=session opentelemetry-instrument shiny run app.py
```

Read the current level in code with `shiny.otel.get_level()`.

## Per-object control: `otel.suppress` / `otel.collect`

Disable Shiny telemetry for sensitive reactives (secrets, PII), or force it on
when the global level is low. Both work as decorators and context managers:

```python
from shiny import otel, reactive, render

@render.text
@otel.suppress  # must be BELOW @render/@reactive (closer to the function)
def result_private():
    return authenticate(input.username(), input.password())

with otel.suppress():
    @reactive.calc  # everything created in this block is suppressed
    def sensitive_calc():
        return load_secrets()

    with otel.collect():
        @reactive.calc  # re-enabled despite the outer suppress
        def public_calc():
            return load_public_data()
```

Key semantics:

- The setting is captured when the reactive object is **created**, not when it
  runs. `with otel.suppress():` inside a reactive function body does nothing to
  that reactive's spans.
- `suppress`/`collect` are absolute per-object overrides: they beat
  `SHINY_OTEL_COLLECT` in both directions. Infrastructure spans
  (`session_start`, `session_end`, `reactive_update`) follow only the env var.
- Only Shiny's internal telemetry is affected — spans you create manually are
  always recorded.

## Custom spans for business logic

Use the standard OpenTelemetry API; no Shiny-specific setup needed:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@reactive.calc
def expensive_computation():
    with tracer.start_as_current_span("database_query") as span:
        result = run_query()
        span.set_attribute("query.rows", len(result))
        return result
```

## Common mistakes

- Calling `trace.set_tracer_provider()` in app code under
  `opentelemetry-instrument` → logs `Overriding of current TracerProvider is
  not allowed` and is ignored. Configure via the wrapper + env vars instead.
  (Exception: SDKs that manage OTel themselves, e.g. `logfire.configure()` —
  then run `shiny run app.py` directly, without the wrapper.)
- `@otel.suppress` placed **above** `@reactive.calc`/`@render.*` → `TypeError`.
  It must wrap the plain function, not the reactive object.
- Suppressing at runtime with `with otel.suppress():` inside a reactive body →
  no effect on that reactive's Shiny spans; the level was captured at creation.
- Traces show `service.name: unknown_service` → set `OTEL_SERVICE_NAME`.
- No Shiny spans at all → check the app was launched under
  `opentelemetry-instrument`, and that `SHINY_OTEL_COLLECT` is not `none`.
- Too much overhead in production → lower `SHINY_OTEL_COLLECT` to `session` or
  `reactive_update`, and/or sample with
  `OTEL_TRACES_SAMPLER=parentbased_traceidratio` + `OTEL_TRACES_SAMPLER_ARG=0.1`.

See `shiny/otel/__init__.py`'s module docs and `examples/open-telemetry/` in
the shiny repo for backend-specific configuration (Jaeger, Logfire, Honeycomb,
Datadog, New Relic).
