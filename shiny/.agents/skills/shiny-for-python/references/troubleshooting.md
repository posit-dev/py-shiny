# Troubleshooting Shiny for Python apps

## Overview

Start with the app's symptoms, code, and existing tests. Identify Core or
Express mode and preserve the app's public behavior and IDs. Read only the
topic guides needed for the diagnosis; do not load every reference upfront.

Troubleshooting routes symptoms to likely causes and repairs.
[Debugging](debugging.md) explains how to observe live inputs, outputs, and
reactive values. [Testing](testing.md) explains how to verify behavior through
a connected browser; [test-server](test-server.md) covers server logic in memory.

## Symptom index

| Symptom | Likely cause and fix | Reference |
|---|---|---|
| Blank output in a Core app | Renderer ID differs from the UI placeholder. Match the function name or use `@output(id=...)`. | [Core output IDs](dynamic-ui.md#output-ids-in-core) |
| Output shows a function object, or a condition is always truthy | Reactive value or calculation was referenced without calling it. Read with `val()`. | [Reactivity](reactivity.md#common-mistakes) |
| One user's state appears in another session | User state was placed in shared scope. In Core, create it in `server()`; in Express, use `app.py`'s per-session scope. | [Session lifecycle](session-lifecycle.md#common-mistakes), [Express shared objects](express.md#shared-objects-and-startup-cost) |
| Session freezes during slow work | A callback holds up reactive processing, or synchronous work blocks the event loop. Use an extended task and offload blocking work. | [Extended tasks](extended-tasks.md#common-mistakes) |
| Reactive loop, repeated writes, or action runs at startup | Side effects in a calc or unintended dependencies in an effect. Keep calcs pure and gate actions with `@reactive.event`. | [Reactivity](reactivity.md#common-mistakes) |
| A list or dictionary changes but outputs stay stale | In-place mutation does not invalidate readers. Set a new copy. | [Reactivity](reactivity.md#updating-collections) |
| `RuntimeError: No current reactive context` | A reactive was read outside a render, calc, effect, or `isolate()` block. | [Reactivity](reactivity.md#common-mistakes) |
| Module outputs stay blank or instances collide | Core UI/server instance IDs differ, or instance IDs are reused. | [Core modules](modules-core.md#common-mistakes), [Express modules](modules-express.md#common-mistakes) |
| Duplicate element IDs or unexpected input/output overrides | IDs must be unique within each namespace. | [Core UI IDs](dynamic-ui.md#output-ids-in-core), [Core modules](modules-core.md#common-mistakes), [Express modules](modules-express.md#common-mistakes) |
| `App(...)` in Express, duplicate UI, or mode syntax errors | Core and Express patterns were mixed. Pick the app's mode and use its API. | [Express](express.md#common-mistakes) |
| R syntax such as `shinyApp`, `fluidPage`, or `observeEvent` | R idioms were copied into Python. Use the Python equivalents. | [Express](express.md#r-shiny-syntax-in-python) |

## Repair and verification workflow

1. Reproduce the symptom and follow its topic reference. Use the debugging
   snapshot tools if the cause depends on live state, then make a targeted fix.
   An import check can catch syntax errors but does not run a Shiny session.
2. Exercise the repaired behavior using an existing connected browser test with
   `shiny.pytest` fixtures. If launching Shiny separately, use a managed process,
   a readiness timeout, and cleanup, then connect a browser or Playwright client.
   Check session initialization, rendered outputs, and input-triggered updates.
   A passing connected test also verifies startup; a separate probe is unnecessary.
3. For session leaks or blocking work, exercise two connected sessions. While
   the slow task runs, check that inputs are captured at invocation time and
   that another session stays responsive. Preserve required service results
   and latency. In-memory server tests can supplement this verification.
4. Run relevant regression tests and stop any processes you started. Rerun a
   passing focused suite only after a code change.

For a broad audit, work through the symptom categories above. If startup is
slow, measure process startup separately from time to first output in a new
session; check shared initialization in [Express](express.md#shared-objects-and-startup-cost)
and deferred work in [extended tasks](extended-tasks.md).

If Playwright fails with `EPERM` while resolving a symlinked Node driver,
retry once with `NODE_OPTIONS='--preserve-symlinks-main --preserve-symlinks'`
or a valid `PLAYWRIGHT_NODEJS_PATH`. Keep searches bounded to relevant app
or package Python files; exclude minified JavaScript and source maps.

Report exactly what ran:

- **Runtime Verified (Session Level)**: connected tests passed for the repair.
- **Server Startup Verified**: the server started, but connected behavior was
  not exercised.
- **Static Diagnosis Only**: runtime execution was unavailable.
