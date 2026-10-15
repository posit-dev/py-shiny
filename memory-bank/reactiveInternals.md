---
title: "Reactive Internals"
description: "Deep dive into the reactive engine in shiny/reactive/ (Context lifecycle, the flush loop, priorities, async, locking, ExtendedTask, poll, error handling, teardown). Read before changing anything in shiny/reactive/ or the session code that drives flushes."
---

# Reactive Internals

The high-level model (Context / Dependents / ReactiveEnvironment, push-pull) is
in [architecture.md](architecture.md#reactive-system). This doc covers the
mechanics, invariants, and gotchas. Files: `shiny/reactive/_core.py` (graph
machinery), `_reactives.py` (`Value`, `Calc_`, `Effect_`, `event`),
`_extended_task.py`, `_poll.py`, `_utils.py` (`is_user_code_frame`, which
OTel name inference uses). Tests: `tests/pytest/test_reactives.py`.

## Context lifecycle (`_core.Context`)

- One `Context` per *execution* of a consumer. `Calc_.update_value()` and
  `Effect_._run()` create a fresh one every run; a context is never reused.
- `id` comes from `ReactiveEnvironment.next_id()`, a monotonic global counter
  (process-wide, shared by every session).
- `invalidate()` is one-shot: it sets `_invalidated`, calls the
  `on_invalidate` callbacks **synchronously**, then clears them. Calling it
  again is a no-op.
- `on_invalidate(f)` on an already-invalidated context calls `f` right away.
- `on_flush(f)` / `add_pending_flush(priority)`: only `Effect_` uses these.
  `execute_flush_callbacks()` awaits each flush callback in order.
- The current context lives in a `ContextVar` (`_current_context`).
  `get_current_context()` raises `RuntimeError("No current reactive context")`
  when there isn't one, so reading a `Value` or `Calc` outside a reactive
  consumer or `isolate()` raises.

## Dependents and invalidation propagation

- `Dependents.register()` adds the current context, keyed by id, and adds an
  `on_invalidate` callback that removes it again. Registering the same context
  twice is a no-op.
- `Dependents.invalidate()` invalidates the dependents in **ascending context
  id** order (oldest first). It works on a snapshot list because callbacks
  change the dict during the loop (issue #26).
- Invalidation is push, and it all runs inside the `set()` call:
  `Value._set` → `Dependents.invalidate` → `Context.invalidate` →
  `Calc_._on_invalidate_cb` (marks the calc invalid, clears the cached value,
  invalidates the calc's dependents) → `Effect_`'s `on_invalidate_cb` →
  `ctx.add_pending_flush(priority)`. Nothing re-runs until a flush happens.
- `Value` keeps two dependent sets: `_value_dependents` (`get()`) and
  `_is_set_dependents` (`is_set()`). The second set is invalidated only when
  the value moves between set and `MISSING`.
- Calcs are lazy. `get_value()` re-runs the calc only if it is `_invalidated`
  or `_running`; the `_running` case handles a calc that calls itself.
  Effects are eager: they enqueue themselves when invalidated.

## Flush loop and priorities (`ReactiveEnvironment`)

- `_reactive_environment` is one module-level singleton for the whole
  process: every session and every App shares it.
- `flush()` opens a `reactive_update` OTel span, runs `_flush_sequential()`,
  then calls the `on_flushed` callbacks.
- `_flush_sequential()` keeps calling `get()` on a `PriorityQueueFIFO` until
  the queue is empty. Effects invalidated *during* the flush join the same
  flush, and a newly queued higher-priority effect jumps ahead of the
  lower-priority effects still waiting.
- `PriorityQueueFIFO` (`shiny/_datastructures.py`): higher priority comes out
  first; equal priorities come out in insertion order. Because
  `Dependents.invalidate` goes oldest-context-first, equal-priority effects
  roughly run in the order of their last execution.
- Priority only matters for effects, and that includes output observers:
  `Outputs` wraps every renderer in an `@effect(priority=...)`.
  `Effect_.set_priority()` only applies from the next invalidation onward.
- Sessions get output flushing through this hook: in its `init` handler,
  `AppSession._run_impl` registers `self._flush` with
  `reactive._core.on_flushed`. So **every flush runs every live session's
  `_flush`**. `App._request_flush` is a stub with a TODO about reactive
  domains.
- Busy/idle: when an effect is enqueued, it calls
  `session._increment_busy_count()`. Its flush callback calls
  `_decrement_busy_count()` even if the effect was destroyed in between. A
  suspended effect doesn't increment the count until `resume()`.

## Async calcs and effects

- Everything is async inside the engine: `_utils.wrap_async` wraps sync
  functions. `flush` **awaits each effect one after another**, so an effect
  that awaits I/O blocks the rest of the queue. Because the global lock is
  held (see below), it also blocks message handling for every session in the
  process. `ExtendedTask` is the escape hatch for this.
- `Effect_._run` runs `await asyncio.sleep(0)` after the user function so
  queued messages can go out (issue #1381).
- A sync `Calc_.__call__` drives `get_value()` through `run_coro_sync`. If
  anything in the chain really yields (for example a sync calc that calls an
  async calc), it raises `RuntimeError("async function yielded control...")`.
  `CalcAsync_.__call__` is `async` and must be awaited.

## Concurrency: `reactive.lock()`

- `lock()` returns a global `asyncio.Lock`. It is created lazily on the first
  call (it needs a running loop) and is **not reentrant**.
- `AppSession._run_impl` holds the lock while it handles each incoming
  message, including the `reactive_flush()` that follows. `invalidate_later`
  and `ExtendedTask._done_callback` take the lock before they
  invalidate and flush.
- `reactive.flush()` does **not** take the lock itself. Code that changes the
  graph from a different task (a background task, a thread bridged back to
  the loop) has to wrap `set()` + `flush()` in `async with reactive.lock()`.
- Concurrency reimplementation: this branch has nothing for it. The name
  `_flush_sequential` is left over from a 2021 option that ran observers
  concurrently, which commit `4bcb11e6b` ("Only allow serial execution of
  reactive observers") removed.

## isolate, event

- `isolate()` sets a brand-new, throwaway `Context` as current. Reads register
  against that context, which is never invalidated, so they create no real
  dependency. The source cleans the entry up the next time it invalidates.
- `event(*args, ignore_none=True, ignore_init=False)` wraps the user
  function. It reads every `arg` in the **caller's** context (those reads are
  the only dependencies), then runs the user function under `isolate()`.
  `req(False)` cancels the run if `ignore_init` is set and this is the first
  run, or if every arg value is `None` or an `ActionButtonValue == 0`
  (`_is_none_event`).
- `event` has to be the innermost decorator. It raises `TypeError` if it
  wraps a `Calc_` or a `Renderer`, if a sync function gets async args, or if
  it has no args.

## invalidate_later, poll, file_reader

- `invalidate_later(delay)` needs a current context. It starts a task that
  sleeps until a monotonic deadline, then, **holding the lock**, calls
  `ctx.invalidate()` and `flush()` (inside `detached_otel_context` so the span
  is a root span). The task is cancelled if the context is invalidated
  earlier or the session ends (`session.on_ended`). Once the task holds the
  lock, `cancellable=False` stops its own `ctx.invalidate()` from cancelling
  it.
- `poll(poll_func, interval_secs)`:
  - It calls `poll_func()` **right away, at decoration time** (isolated) to
    seed `last_value`. An async `poll_func` would seed it with a coroutine
    object.
  - An `@effect(priority=...)` re-polls and compares with `equals`. It puts
    errors in `last_error` and reschedules itself with `invalidate_later` in
    a `finally`.
  - The decorated reader becomes a `calc` that depends on `last_error` and
    `last_value`.
  - When `poll` is created outside a session (at module level), the effect
    has no session, so nothing ever tears it down. That's intentional: one
    poller for the whole process.
- `file_reader` is `poll` with `check_timestamp`, which returns
  `(path, mtime, size)`. Its default `priority=1` (poll's is 0). A missing
  file raises inside the effect, the error is saved, and every reader
  re-raises it.

## ExtendedTask (`_extended_task.py`)

- `Status = "initial" | "running" | "success" | "error" | "cancelled"`.
  `status`, `value`, and `error` are `Value`s (created under
  `otel.suppress()`).
- `invoke()` runs under `isolate()`, so calling it doesn't create a
  dependency on `status`. If a run is in progress or calls are already
  queued, it adds a closure to `_invocation_queue`; queued calls run in FIFO
  order, one at a time. `_invoke` asserts `_task is None`, sets `running`,
  unsets `value`/`error`, and calls `asyncio.create_task(_execution_wrapper)`.
- `_execution_wrapper` runs the user coroutine under a `DenialContext`. Its
  `on_invalidate` raises, so **any** reactive read inside the task raises
  `RuntimeError`. This also protects against the `ContextVar` the task
  inherited from the effect that started it.
- `_done_callback` sets `_task = None` and starts a strong-referenced task
  (`_done_tasks`; the event loop only keeps weak references). That task takes
  the lock, sets `status`/`value`/`error`, flushes, then pops the next queued
  call and flushes again.
- `cancel()` clears the queue and cancels the running task. The status then
  becomes `cancelled` through `_done_callback`.
- `result()`: `success` returns the value and `error` re-raises the error.
  `running` raises `req(False, cancel_output="progress")`
  (`SilentOperationInProgressException`); the output keeps its old value and
  shows progress. `initial` and `cancelled` raise a plain `SilentException`.
- Sessions: an ExtendedTask has **no `on_ended` hook**, so a running task
  keeps going after the session closes. Its `Value`s survive session close
  on purpose (see Teardown) so the late completion doesn't hit
  `DestroyedReactiveError`.

## Error propagation

| Raised in an `Effect_` | Handling in `Effect_._run` |
| --- | --- |
| `SilentException` (+ `SilentOperationInProgressException` subclass) | swallowed |
| `NotifyException` | `notification_show` (sanitized if `e.sanitize`); `session._unhandled_error` if `e.close` |
| any other `Exception` | `ReactiveWarning`, then `session._unhandled_error` → `session.close()` |

- `Calc_._run_func` catches `Exception`, including silent ones, and **caches
  it** in `_error`. Every reader re-raises it until the calc is invalidated.
- `Value.get()` on `MISSING` raises `SilentException`. On a destroyed value
  it raises `DestroyedReactiveError`.
- Output observers (`Outputs.__call__` in `shiny/session/_session.py`)
  handle errors themselves:
  - `SilentOperationInProgressException`: sends progress and returns early,
    with no "recalculated" message.
  - `SilentCancelOutputException`: leaves the output unchanged.
  - `SilentException`: clears the output (`set_silent`).
  - Other errors: sent to the client as an output error, sanitized unless
    it's a `SafeException`.

## Teardown (session end vs destroy)

- `Effect_.__init__` registers a **strong** `session.on_ended(self.destroy)`
  and a weak `on_destroy`. `Value` and `Calc_` register only a weak
  `on_destroy`, built with `_weak_destroy_callback`.
- `AppSession._run_session_ended_tasks`:
  1. Sets `_has_run_session_ended_tasks = True` (this is what `_is_closed()`
     checks).
  2. Calls the `on_ended` callbacks, which destroy every effect.
  3. Calls `self.destroy()`, which runs the `on_destroy` callbacks deepest
     namespace first. The weak destroy callbacks see `session._is_closed()`
     and **no-op**: on close, values and calcs stay readable and are left to
     GC.
- An explicit `session.destroy(id)` or module-scope `destroy()` tears things
  down for real. `Value.destroy()` unsets the value and invalidates both
  dependent sets. `Calc_.destroy()` invalidates its context and clears its
  cache. `Effect_.destroy()` sets `_destroyed` and invalidates its context.
  After that, `input._destroy()` and `output._destroy()` run.
- A destroyed effect can still have a pending queue entry: `on_flush_cb`
  skips `_run()` but still decrements the busy count.

## Pitfalls

- **`Value.set` compares by identity (`is`), not equality.** Setting an equal
  but different object invalidates dependents. Mutating an object in place
  and setting it again does **nothing**; assign a new object instead.
- `Value.unset()`'s docstring says it returns a bool, but it returns `None`.
  `freeze()` unsets the value *without* invalidating dependents.
- Don't take `reactive.lock()` inside an effect, calc, or render function.
  The session already holds it during the flush, and `asyncio.Lock` isn't
  reentrant, so it deadlocks.
- `SilentCancelOutputException` (and `SilentOperationInProgressException`)
  subclass `SilentException`, so an `except SilentException` also catches
  them. Where they need different handling (output observers), catch the
  subclasses first.
- If a `Calc_` is interrupted by a `BaseException` (for example
  `CancelledError`), `_invalidated` stays `False` with no value and no error.
  The next read without an invalidation would hit `IndexError` on
  `_value[0]`.
- When an `Effect_` is created under a stub session (Express UI pass), its
  `__init__` returns early, so the object is half-built and never runs.
- `asyncio.create_task` copies `ContextVar`s, so a task started inside an
  effect still sees that effect's (possibly invalidated) context as current.
  Reactive reads there silently attach to it, or fire immediately. Read
  values before spawning, or use `ExtendedTask`.
- Every flush calls every session's `_flush` (the global `on_flushed`
  hook), so per-session work in `_flush` scales with the number of sessions.
- Effects scheduled before the first flush don't run until something calls
  `flush()`. In tests, call `await reactive.flush()` explicitly.
