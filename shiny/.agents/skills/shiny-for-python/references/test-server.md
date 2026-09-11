# Testing server logic in memory with `test_server()`

## Overview

`shiny.testserver.test_server()` runs an app's server function against a mock
connection — no browser, no network, no Playwright. Set inputs, let the
reactive graph settle, assert on outputs, all in an ordinary (non-async) pytest
test. It is the Python counterpart to R Shiny's `testServer()`.

Use it for server logic: calcs, output values, error paths, modules. Use
Playwright (`references/testing.md`) for anything the user sees or clicks —
layout, widgets, client-side behavior. Do **not** call the server function
directly with hand-built `Inputs`/`Session` objects, and do not launch a
subprocess just to check an output's value.

## Setup

Nothing beyond `pytest`. `test_server` ships with shiny.

## Write a test

```python
# app.py
from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_numeric("n", "N", 10),
    ui.output_text("doubled"),
)

def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def doubled():
        if input.n() < 0:
            raise ValueError("n must be positive")
        return str(input.n() * 2)

app = App(app_ui, server)
```

```python
# test_app.py
from shiny.testserver import test_server

def test_doubles():
    with test_server() as ts:          # app.py beside this test file
        ts.set_inputs(n=10)
        assert ts.is_ok
        assert ts.get_output("doubled") == "20"

        ts.set_inputs(n=21)            # unnamed inputs keep their values
        assert ts.get_output("doubled") == "42"

def test_reports_error():
    with test_server() as ts:
        ts.set_inputs(n=-1)
        assert ts.is_ok is False
        failed = ts.get_output("doubled")
        assert failed.status == "error"
        assert "must be positive" in failed.error
```

The session **must** be used as a context manager; `with` tears the app down
even when an assertion fails. `set_inputs()` flushes the reactive graph before
returning, so outputs are already current — no waiting or retrying.

## What `test_server()` accepts

```python
test_server()                 # "app.py" beside the test file (Core or Express)
test_server("myapp.py")       # another file, relative to the test file
test_server(Path("/abs/app.py"))
test_server(app)              # a shiny.App instance
test_server(server_fn)        # a bare server function, wrapped in an empty-UI app
```

Optional keywords: `client_data=` (see below) and `timeout_secs=5.0` (per
flush, including the initial one — raise it for slow startups such as a cold
matplotlib font cache).

## Values and their status

`get_input()`, `get_output()`, and `get_export()` return a `TestServerValue`
that **compares equal to its underlying value**, so `== "20"` needs no
unwrapping. Each has `.status`, `.value`, `.error`, `.traceback`:

| `status` | Meaning |
|---|---|
| `"ok"` | Rendered; `.value` is the JSON-round-tripped value the browser would receive |
| `"error"` | The render function raised; see `.error` and `.traceback` |
| `"silent"` | Never rendered — a dependency was unavailable (an unset input, or `req()` failed) |

Comparing a non-`"ok"` value with `==` raises `ValueError` rather than
returning `False`, so a broken output cannot pass a `!=` assertion by
accident. Asking for an id that does not exist raises `KeyError`.

`ts.get_export("name")` reads values registered with
`shiny.testmode.export_test_values()` — internal reactives that have no output
(see `references/debugging.md`).

## Modules

Module ids are namespaced, so either use the full id or take a scope:

```python
def test_counter_module():
    with test_server(app_server) as ts:
        ts.set_inputs(**{"counter-n": 7})
        assert ts.get_output("counter-label") == "n=7"

        with ts.make_scope("counter") as counter:   # bare ids inside the module
            counter.set_inputs(n=8)
            assert counter.get_output("label") == "n=8"
```

Nested modules chain: `ts.make_scope("outer").make_scope("inner")`. Express
modules use the same ids.

## Client data (plots and URL readers)

A browser normally reports output sizes, pixel ratio, and URL parts. Without
them `render.plot` and `session.clientdata.url_*()` would be `"silent"`.
`test_server` sends `DEFAULT_CLIENT_DATA` stand-ins automatically; override
when a test cares:

```python
with test_server(client_data={"output_width": 300}) as ts:   # every output
    assert ts.get_output("plot").status == "ok"

with test_server() as ts:                                     # one output, mid-test
    ts.set_inputs(**{".clientdata_output_plot_width": 300})
```

## Snapshots and fixtures

```python
import pytest
from shiny.testserver import test_server

@pytest.fixture            # keep function-scoped: a session remembers its inputs
def ts():
    with test_server("myapp.py") as session:
        yield session

def test_everything(ts):
    ts.set_inputs(n=10)
    values = ts.to_values()   # TestServerValues: .is_ok, .inputs, .outputs, .exports
    as_dict = dict(ts)        # plain JSON-ready data
    assert values.outputs["doubled"].value == "20"
```

Both forms are copies and stay valid after the `with` block closes.

## Async tests

`test_server()` drives its own event loop and cannot run inside a running one.
In an `async def` test use `test_server_async()` — same API, but `async with`
and `await ts.set_inputs(...)` / `await ts.flush()`.

## Common mistakes

- `RuntimeError` about a running event loop → the test is `async`; switch to
  `test_server_async()`.
- Output is `"silent"` → an input it reads was never set, or a `req()` failed.
  Set the input, then read again.
- `KeyError` for a module's output → the id is namespaced
  (`"counter-label"`), or use `make_scope("counter")`.
- Tests interfere with each other → the fixture is module- or session-scoped;
  make it function-scoped.
- `TimeoutError` on startup → the app is slow to import; raise `timeout_secs=`.
- Forgot the `with` → the session never starts. `test_server()` returns an
  unstarted session; always enter it.
