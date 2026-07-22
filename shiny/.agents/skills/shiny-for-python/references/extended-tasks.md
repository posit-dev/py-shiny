
# Extended tasks in Shiny for Python

## Overview

A slow computation inside a `@reactive.calc`, `@reactive.effect`, or `@render.*`
blocks the reactive flush - even an `async def` one - so the whole session (and,
for shared resources, other sessions) freezes until it returns. Do NOT put a
slow API call, model inference, or long loop directly in a calc/effect.

`@reactive.extended_task` runs an **async** function in a background asyncio
task, off the reactive flush. Reactivity keeps processing while it runs; the
result flows back into the reactive graph when it finishes.

Because it runs outside the reactive flush, the task **cannot read reactive
sources** (`input.x()`, a `reactive.value`, a calc). Read those values *before*
invoking and pass them in as arguments; reading one inside raises an error.

## Define and invoke a task

Decorate an async function. Call the returned object (or `.invoke(...)`) from an
effect - usually gated on a button - passing any reactive values as arguments.

```python
import asyncio
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_numeric("x", "x", 1),
    ui.input_numeric("y", "y", 2),
    ui.input_task_button("run", "Compute, slowly"),
    ui.output_text("result"),
)

def server(input, output, session):
    @reactive.extended_task
    async def slow_sum(a: int, b: int) -> int:
        await asyncio.sleep(3)          # stand-in for a slow API / model call
        return a + b

    @reactive.effect
    @reactive.event(input.run)
    def _():
        slow_sum(input.x(), input.y())  # read inputs HERE, pass as args

    @render.text
    def result():
        return str(slow_sum.result())   # read result in a reactive context

app = App(app_ui, server)
```

`.invoke(*args)` returns immediately (`None`). `slow_sum(...)` is shorthand for
`slow_sum.invoke(...)`.

## Read the result and status

- `task.result()` - call inside a reactive context (a `@render.*`, calc, or
  effect). On success it returns the value; on error it re-raises; while running
  or before the first run it raises a silent exception that leaves the output
  blank or in a progress state. Reading it establishes a reactive dependency, so
  outputs update automatically when the task finishes.
- `task.status()` - a reactive read returning `"initial"`, `"running"`,
  `"success"`, `"error"`, or `"cancelled"`. Use it to drive conditional UI.

```python
@render.ui
def status_msg():
    if slow_sum.status() == "running":
        return ui.markdown("Working...")
    return None
```

## Pair with a task button

`ui.input_task_button` auto-disables and shows a busy label on click, then
resets when reactive processing settles. `ui.bind_task_button` keeps it busy for
the task's full lifetime - place it above `@reactive.extended_task`:

```python
    @ui.bind_task_button(button_id="run")
    @reactive.extended_task
    async def slow_sum(a: int, b: int) -> int:
        ...
```

Binding does not invoke the task - you still need the effect. For manual
control, call `ui.update_task_button("run", state="busy" | "ready")`, or pass
`auto_reset=False` to keep the button busy until you reset it yourself.

## Cancel and re-invoke

`task.cancel()` cancels the running invocation (status becomes `"cancelled"`)
and clears any queued invocations. Invoking again while a run is in progress
does **not** interrupt it - the new call is **queued** and runs after the
current one finishes.

```python
    @reactive.effect
    @reactive.event(input.cancel)
    def _():
        slow_sum.cancel()
```

## Quick reference

| Need | Use |
|---|---|
| Mark an async fn as background work | `@reactive.extended_task` |
| Start a run (non-blocking) | `task(args)` / `task.invoke(args)` |
| Get the result reactively | `task.result()` (in a reactive context) |
| Check state | `task.status()` -> initial/running/success/error/cancelled |
| Stop the current + queued runs | `task.cancel()` |
| Auto busy button | `ui.input_task_button("id", ...)` + `@ui.bind_task_button(button_id="id")` |
| Manual button state | `ui.update_task_button("id", state="busy"/"ready")` |

## Common mistakes

- Reading `input.x()` / a `reactive.value` inside the task body -> raises "not
  allowed to read reactive sources". Read before invoking; pass as arguments.
- Decorating a plain `def` -> `TypeError`; the function must be `async def`.
- Long synchronous work (a blocking library call) inside the async task still
  blocks the event loop - offload it with `asyncio.to_thread(...)` or an async
  client.
- Calling `task.result()` outside a reactive context -> no dependency is tracked
  and it errors; read it inside a `@render.*`, calc, or effect.
- Expecting a fresh `.invoke()` to interrupt the running task -> it queues
  instead; call `.cancel()` first if you need to abort.
- Awaiting `.invoke()` or using its return value -> it returns `None`
  immediately; get output via `.result()`.
</content>
</invoke>
