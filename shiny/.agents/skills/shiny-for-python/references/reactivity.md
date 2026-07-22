
# Reactivity in Shiny for Python

## Overview

Shiny builds a dependency graph automatically: reading a reactive source
(`input.x()`, a `reactive.value`, a `@reactive.calc`) inside a reactive context
registers a dependency, so when that source changes, everything that read it
re-runs. You do not call outputs or schedule updates yourself.

Do NOT recompute non-trivial work in every output, poll in a `while` loop, or
read `input.x()` at module top level or inside a plain helper. Reactive sources
are only readable inside a reactive context: a `@render.*` output, a
`@reactive.calc`, a `@reactive.effect`, or an `isolate()` block. For work that
blocks the session (a slow API call, a long computation), do not run it in a
calc/effect either — use `reactive.extended_task` (see `references/extended-tasks.md`).

## Share a mutable value: `reactive.value`

A settable reactive source. Read with `()` or `.get()`; write with `.set()`.
Writing invalidates every reader.

```python
from shiny import reactive

count = reactive.value(0)

@reactive.effect
@reactive.event(input.increment)
def _():
    count.set(count() + 1)   # read current, write new
```

## Cache a derived value: `@reactive.calc`

Use a calc for a value derived from other reactive sources. It is **cached**:
it runs once, memoizes, and re-runs only when a dependency invalidates. Many
outputs can call it without repeating the work.

```python
@reactive.calc
def filtered():
    return df[df["group"] == input.group()]

@render.data_frame
def table():
    return filtered()          # cheap; computed once per change

@render.text
def n_rows():
    return f"{filtered().shape[0]} rows"
```

## Perform a side effect: `@reactive.effect`

Use an effect for actions with no return value: updating inputs, writing files,
`ui.insert_ui`, logging. Effects run automatically when a dependency changes.

```python
@reactive.effect
def _():
    ui.update_select("city", choices=cities_for(input.country()))
```

Rule of thumb — pick by what the code produces:

- `@reactive.calc` — cache an intermediate value other code reads.
- `@render.*` — display a value in the UI.
- `@reactive.effect` — perform a side effect (no return value).

Never put display logic in an effect.

## Control when reactivity fires: `@reactive.event`

Place it below `@reactive.effect`/`@reactive.calc`/`@render.*` to restrict
dependencies to the listed events only. The body may read other reactive
values without depending on them.

```python
@reactive.effect
@reactive.event(input.submit)        # runs ONLY when submit is clicked
def _():
    save(input.name(), input.email())  # read, but don't react to, these
```

`ignore_none=True` (default) skips runs when the event is `None`/`0`;
`ignore_init=True` skips the initial run on load.

## Short-circuit / validate: `req()`

Stops execution when a value is missing (falsy), silently pausing dependent
outputs until the requirement is met.

```python
from shiny import req

@render.text
def greeting():
    req(input.name())               # wait until name is non-empty
    return f"Hello, {input.name()}"
```

Use `req(x, cancel_output=True)` to keep the previous output visible instead of
blanking it.

## Read without depending: `isolate()`

Read a reactive source without registering a dependency, so changes to it do
not trigger a re-run.

```python
@reactive.effect
@reactive.event(input.go)
def _():
    with reactive.isolate():
        seed = input.seed()        # used, but does not trigger re-runs
    run_model(seed)
```

## Timers and streaming: `invalidate_later`, `poll`, `file_reader`

Invalidate on a timer (re-runs the containing context after N seconds):

```python
@reactive.effect
def _():
    reactive.invalidate_later(1)   # tick every second
    tick.set(tick() + 1)
```

Stream from a data source without a loop. `poll` runs a cheap check on an
interval and re-reads only when it changes; `file_reader` watches a file's
mtime/size:

```python
@reactive.poll(lambda: os.path.getmtime(path), interval_secs=1)
def data():
    return pd.read_csv(path)

@reactive.file_reader(path)        # same idea, file-aware
def data2():
    return pd.read_csv(path)
```

Declare `poll`/`file_reader` at module top level to share one cache across
sessions.

(For long-running async work that must not block the session, see
`reactive.extended_task` - out of scope here.)

## Quick reference

| Need | Use |
|---|---|
| Settable reactive value | `v = reactive.value(x)`; `v()` / `v.set(x)` |
| Cached derived value | `@reactive.calc` |
| Side effect (update UI, log, write) | `@reactive.effect` |
| Fire only on a specific event | `@reactive.event(input.btn)` |
| Wait for / validate a value | `req(x)`, `req(x, cancel_output=True)` |
| Read without depending | `with reactive.isolate():` |
| Timer | `reactive.invalidate_later(secs)` |
| Poll a data source / file | `@reactive.poll(...)` / `@reactive.file_reader(...)` |
| Force sync execution in tests | `reactive.flush()` |

## Common mistakes

- `input.x()` read at module scope or in a plain helper -> "no current
  reactive context" error. Read it inside a `@render.*`, `calc`, `effect`, or
  `isolate()`.
- Non-trivial computation duplicated across outputs -> wrap it in a
  `@reactive.calc` and call that from each output.
- Using a `@reactive.effect` to compute a displayed value -> effects return
  nothing; use a `calc` or `@render.*` function.
- Effect re-runs on every incidental input change -> add
  `@reactive.event(...)` (below the effect decorator) to pin the trigger.
- Reading a `reactive.value` you also `.set()` in the same effect without
  `isolate()` -> self-invalidating loop; wrap the read in `reactive.isolate()`.
- `while`/`sleep` loop to watch a DB or file -> use `reactive.poll` or
  `reactive.file_reader`.
