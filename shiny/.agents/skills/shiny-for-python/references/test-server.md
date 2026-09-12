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
# test_app.py -- `local_server` is a built-in pytest fixture; nothing to import
def test_doubles(local_server):        # app.py beside this test file
    local_server.set_inputs(n=10)
    assert local_server.is_ok
    assert local_server.get_output("doubled") == "20"

    local_server.set_inputs(n=21)      # unnamed inputs keep their values
    assert local_server.get_output("doubled") == "42"

def test_reports_error(local_server):
    local_server.set_inputs(n=-1)
    assert local_server.is_ok is False
    failed = local_server.get_output("doubled")
    assert failed.status == "error"
    assert "must be positive" in failed.error
```

`local_server` is an already-started `test_server()` session for the `app.py`
next to the test file, torn down by pytest. It is function-scoped — every test
gets a fresh session — and takes another file via
`@pytest.mark.parametrize("local_server", ["other_app.py"], indirect=True)`.
`set_inputs()` flushes the reactive graph before returning, so outputs are
already current — no waiting or retrying.

Call `test_server()` directly when the fixture cannot express what you need:
a server function or `App` object, `client_data=`, `timeout_secs=`. The
session **must** then be used as a context manager; `with` tears the app down
even when an assertion fails:

```python
from shiny.testserver import test_server

def test_doubles():
    with test_server("myapp.py") as ts:
        ts.set_inputs(n=10)
        assert ts.get_output("doubled") == "20"
```

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
| `"silent"` | The latest render produced nothing, so the browser blanks it — a dependency was unavailable (an unset input, or `req()` failed) |
| `"never-rendered"` | Has not run at all yet, so it has produced no value, error, or silent render |

Comparing a non-`"ok"` value with `==` raises `ValueError` rather than
returning `False`, so a broken output cannot pass a `!=` assertion by
accident. Asking for an id that does not exist raises `KeyError`.

`"silent"` describes the *latest* render: an output that rendered once and is
then silenced by a failing `req()` reports `"silent"` with no value, matching
the blank the browser shows rather than the stale value.

`ts.get_export("name")` reads values registered with
`shiny.testmode.export_test_values()` — internal reactives that have no output
(see `references/debugging.md`).

## Modules

Module ids are namespaced, so either use the full id or take a scope:

```python
def test_counter_module(local_server):
    local_server.set_inputs(**{"counter-n": 7})
    assert local_server.get_output("counter-label") == "n=7"

    counter = local_server.make_scope("counter")   # bare ids inside the module
    counter.set_inputs(n=8)
    assert counter.get_output("label") == "n=8"
```

Nested modules chain: `local_server.make_scope("outer").make_scope("inner")`.
Express modules use the same ids.

A module server can be tested without any app file — `test_server(app_server)`
wraps the bare server function in an empty-UI app. See "Snapshots and
fixtures" for the fixture shape.

## Client data (plots and URL readers)

A browser normally reports output sizes, pixel ratio, and URL parts. Without
them `render.plot` and `session.clientdata.url_*()` would be `"silent"`.
`test_server` sends `DEFAULT_CLIENT_DATA` stand-ins automatically; override
when a test cares:

```python
def test_plot_size(local_server):                        # one output, mid-test
    local_server.set_inputs(**{".clientdata_output_plot_width": 300})
    assert local_server.get_output("plot").status == "ok"

def test_every_plot_size():                              # every output, up front
    with test_server(client_data={"output_width": 300}) as ts:
        assert ts.get_output("plot").status == "ok"
```

## Snapshots and fixtures

`local_server` covers an `app.py` beside the test file. For anything else
(`client_data=`, `timeout_secs=`, a server function or `App` object), write a
fixture of your own around `test_server()`:

```python
import pytest
from shiny.testserver import test_server

@pytest.fixture            # keep function-scoped: a session remembers its inputs
def ts():
    with test_server(app_server) as session:
        yield session

def test_everything(ts):
    ts.set_inputs(n=10)
    values = ts.to_values()   # TestServerValues: .is_ok, .inputs, .outputs, .exports
    as_dict = dict(ts)        # plain JSON-ready data
    assert values.outputs["doubled"].value == "20"
```

Both forms are copies and stay valid after the session is torn down.

## Async tests

`test_server()` drives its own event loop and cannot run inside a running one.
In an `async def` test use `test_server_async()` — same API, but `async with`
and `await ts.set_inputs(...)` / `await ts.flush()`.

## Common mistakes

- `RuntimeError` about a running event loop → the test is `async`; switch to
  `test_server_async()`.
- Output is `"silent"` → an input it reads was never set, or a `req()` failed.
  Set the input, then read again.
- Output is `"never-rendered"` → it has not run at all, usually because it is
  hidden and so suspended. Make it visible (e.g. drop `output_hidden` from
  `client_data=`).
- `KeyError` for a module's output → the id is namespaced
  (`"counter-label"`), or use `make_scope("counter")`.
- Tests interfere with each other → the fixture is module- or session-scoped;
  make it function-scoped.
- `TimeoutError` on startup → the app is slow to import; raise `timeout_secs=`.
- Forgot the `with` → the session never starts. `test_server()` returns an
  unstarted session; always enter it — or use `local_server`, which is already
  started.
