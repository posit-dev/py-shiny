---
name: debugging
description: Use when observing server-side state of a Shiny for Python (py-shiny) app - inspecting reactive/calc values in a running session, capturing current input/output state, exposing internal values to a test harness, asserting server-side values in snapshot tests, or when tempted to add print statements or hidden outputs to see server-side values. (For writing Playwright end-to-end tests against the rendered UI, use the testing skill.)
---

# Debugging Shiny for Python apps

## Overview

py-shiny has a built-in **test mode**: every session can serve a read-only JSON
snapshot of its `input`, `output`, and `export` values over HTTP. Use it instead
of print statements, hidden outputs, or websocket spelunking to observe
server-side state.

## Enable test mode

- Env var: `SHINY_TESTMODE=1 shiny run app.py`
- Or in code: `App(app_ui, server, test_mode=True)`
- The pytest app-launch fixtures (`local_app`, `create_app_fixture`) enable it
  automatically.

When off, the snapshot endpoint returns 404 and the APIs below are cheap no-ops,
so calls can be left in production code.

## Read a session snapshot

Each session serves `GET /session/{id}/dataobj/shinytest` returning
`{"input": {...}, "output": {...}, "export": {...}}` with sorted keys.

**Getting the URL:** the session id only exists after the client connects — do
not guess it or scrape it from the page. Obtain the URL through one of two
paths:

1. **From the browser** (devtools console, browser automation) — ask the Shiny
   client, then GET the result from the page context (so any auth
   cookies/headers come along):

   ```js
   window.Shiny.shinyapp.getTestSnapshotBaseUrl({ fullUrl: true })
   // -> "http://127.0.0.1:8000/session/<id>/dataobj/shinytest?w=...&nonce=..."
   ```

   This is undefined until the app has connected; wait for it to exist before
   calling. (In Playwright, prefer `AppTestValues` below, which handles the
   waiting and fetching.)

2. **From server code** (inside the `server` function, where `session` is in
   scope) — `session.get_test_snapshot_url()` returns the relative URL with a
   cache-busting nonce; log it or surface it to wherever you need it.

Select blocks with query params: `?input=1` (whole block), `?output=a,b`
(specific keys); no params returns all three blocks.

Values that fail to serialize appear as visible markers instead of erroring:
`{"__shiny_serialization_error__": ...}`, output render errors as
`{"__shiny_output_error__": ...}`, preprocessor failures as
`{"__shiny_snapshot_preprocess_error__": ...}`.

## Expose internal reactive values: `export_test_values()`

To let a test harness read a `reactive.calc` or other internal value (do NOT
render it into a hidden output):

```python
from shiny import App, Inputs, Outputs, Session, reactive, ui
from shiny.testmode import export_test_values

app_ui = ui.page_fluid(ui.input_slider("n", "n", 0, 100, 20))

def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def doubled():
        return input.n() * 2

    # Appears under "export" in the snapshot. No-op unless test mode is on.
    export_test_values(doubled=doubled, plus_one=lambda: doubled() + 1)

app = App(app_ui, server)
```

Each value is a zero-argument callable, evaluated lazily (in a reactive
isolate) when a snapshot is requested. Inside a module, export names are
namespaced with the module's `ns` prefix. Re-registering a name overwrites it.

## Assert snapshot values in Playwright tests

```python
from shiny.playwright import controller

app_values = controller.AppTestValues(page)
app_values.expect_input("n", 20)
app_values.expect_output("greeting", "Hello abc")
app_values.expect_export("doubled", 40)
snapshot = app_values.get()  # full {"input", "output", "export"} dict
```

Requires the app loaded in the page and test mode on (a `RuntimeError` with a
fix hint is raised otherwise).

## Scrub unstable values from snapshots

Timestamps, temp paths, etc. make snapshots non-deterministic. Preprocess
before they are written (sync or async functions both work):

- Inputs: `shiny.testmode.snapshot_preprocess_input("secret", lambda v: "<redacted>")`
  or `session.input.set_snapshot_preprocess(id, fn)`
- Outputs: call `.snapshot_preprocess(fn)` on the `@render.*` object
- File inputs automatically scrub each file's `datapath` to its basename

## Other debugging tools

| Need | Tool |
|---|---|
| Verbose framework logs | `SHINY_LOG_LEVEL=DEBUG shiny run app.py` |
| Echo client/server websocket messages | `App(..., debug=True)` |
| Auto-reload during development | `shiny run app.py --reload --launch-browser` |

## Common mistakes

- Hitting the snapshot endpoint without test mode enabled → 404. Set
  `SHINY_TESTMODE=1` or `App(test_mode=True)`.
- Rendering values into hidden outputs just so tests can read them → use
  `export_test_values()` instead.
- Expecting un-namespaced export names inside modules → exports are prefixed
  with the module namespace, like inputs and outputs.
- Snapshot diffs churn on paths/timestamps → add a snapshot preprocessor
  instead of post-processing the JSON.
