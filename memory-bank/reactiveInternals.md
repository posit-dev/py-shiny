---
title: "Reactive Internals"
description: "Deep dive into the reactive engine in shiny/reactive/ (Context lifecycle, rounds and the reactive effect queue, priorities, per-session cycles, concurrent async effects and calcs, reactive.flush(), cancellation on destroy, ExtendedTask, poll, error handling, teardown). Read before changing anything in shiny/reactive/ or the session code that drives rounds and cycles."
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
  `add_pending_flush` puts the context in the reactive effect queue
  (`ReactiveEnvironment.enqueue_effect`, which also calls `request_round()`).
  A round runs `execute_flush_callbacks()` for the context in a task of its
  own (`_run_context`).
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
  `ctx.add_pending_flush(priority)`. Nothing re-runs until the next round.
- `Value` keeps two dependent sets: `_value_dependents` (`get()`) and
  `_is_set_dependents` (`is_set()`). The second set is invalidated only when
  the value moves between set and `MISSING`.
- Calcs are lazy. `get_value()` re-runs the calc only if it is `_invalidated`
  or `_running`; the `_running` case handles a calc that calls itself.
  Effects are eager: they enqueue themselves when invalidated.

## Rounds and priorities (`ReactiveEnvironment`)

The `ReactiveEnvironment` class docstring defines the vocabulary used here:
reactive effect queue, round, idle, cycle, output flush.

- `_reactive_environment` is one module-level singleton for the whole
  process: every session and every App shares one reactive effect queue.
- **Requesting a round.** `enqueue_effect()` calls `request_round()`, which
  schedules `_start_requested_round` with `loop.call_soon(...,
  context=contextvars.Context())`. Requests made before it runs merge into
  one round (`_round_requested`). The fresh `contextvars` context keeps the
  requester's session, current reactive context, and OTel span out of the
  round. From another thread, the request is re-posted with
  `call_soon_threadsafe` to the loop Shiny runs on (`_loop`); only the request
  is thread-safe, `Value.set()` itself must run on the loop's thread. With no
  running loop at all, nothing is scheduled.
- **A round never waits for effects.** `start_round()` pops contexts from the
  `PriorityQueueFIFO` and starts each in its own task (`_spawn(_run_context(ctx))`),
  yielding once per effect (`_yield_to_loop`) so the task's sync part runs and
  anything it invalidates is queued before the next pop. A newly queued
  higher-priority effect still jumps ahead of waiting ones. Priority orders
  effect *starts*, not finishes. After the queue drains, the round awaits the
  round-finished callbacks (public `reactive.on_flushed()`; errors are printed
  and don't skip the rest).
- **No nesting.** If a round is requested while one runs, `start_round()` sets
  `_rerun_round` and returns; the running round's `finally` calls
  `request_round()` again (a no-op if a request is already pending, so there
  is exactly one extra round).
- **Strong refs.** `_spawn()` keeps every round, effect, and session output
  flush task in `_tasks` (the loop holds only weak refs). `_on_task_done`
  prints a traceback for an escaped exception; effects report their own errors
  before that (see Error propagation). `_adopt_loop()` discards round state
  left on a stopped loop (repeated `test_server()` runs).
- `PriorityQueueFIFO` (`shiny/_datastructures.py`): higher priority comes out
  first; equal priorities come out in insertion order. Because
  `Dependents.invalidate` goes oldest-context-first, equal-priority effects
  roughly start in the order of their last execution.
- Priority only matters for effects, and that includes output observers:
  `Outputs` wraps every renderer in an `@effect(priority=...)`.
  `Effect_.set_priority()` only applies from the next invalidation onward (the
  run keeps its `queued_priority`, which the bookmark restore gate also uses).
- **Session output flushes.** `App._request_output_flush(session)` records the
  session in `_sessions_needing_output_flush`, lazily registers
  `App._start_output_flushes` as a round-finished callback, and requests a
  round. After the round, each recorded session starts its own output flush
  task (`AppSession._start_output_flush`), so only sessions that asked are
  touched. The hook is unregistered when the app's last session is removed
  (`App._remove_session`). See [sessionMessaging.md](sessionMessaging.md#cycles-and-the-output-flush).

## Cycles and the busy count

- A **cycle** is per session: one cycle start action, the effects it starts,
  and the output flush that ends it. `Effect_._create_context`'s
  `on_invalidate_cb` calls `session._increment_busy_count()` when it queues
  the effect; `on_flush_cb`'s `finally` calls `_decrement_busy_count()` on
  every exit path (ran, destroyed, raised, cancelled). A suspended effect
  doesn't increment the count until `resume()`.
- 0 → 1 sends `busy` and starts the cycle's `reactive_update` span; 1 → 0 ends
  it, sends `idle`, sets `_cycle_ended`, and requests an output flush. The
  span is per session cycle, not per round; details in
  [otel.md](otel.md).
- **Cycle start actions** (`_cycle_start_action_queue`): input `update`
  messages (`functools.partial(self._manage_inputs, data)`) and
  `invalidate_later` timers queue through `session.run_once_when_idle(fn)`.
  Only `_output_flush` runs them, via `_start_cycle()`, one per cycle, after
  the previous cycle's outputs are sent and only while `_busy_count == 0`.
  They never run inline in the task that queued them. So effects paused at
  an `await` see stable inputs.
- `run_once_when_idle(fn)` is public. `fn` must be sync (`_validate_idle_action`
  raises `TypeError` for an async callable), runs under `session_context`
  (a `SessionProxy` wraps it in its own scope's context), its return value is
  ignored, and an error it raises is printed and closes the session. Calls
  after the session ended are dropped right away; queued actions are cleared
  if the session ends first. `ExpressStubSession.run_once_when_idle` is a
  no-op. The base `Session.run_once_when_idle` raises `NotImplementedError`.

## `reactive.flush()` / `run_until_idle()`

- Public `reactive.flush()` is `run_until_idle()`: it repeatedly
  `run_next_round()`s and then `asyncio.wait`s on every live task in `_tasks`
  (excluding itself) until the queue is empty, no task is running, and no
  round is requested. That covers effects' async parts and every session's
  output flush, process-wide, so busy activity in another session delays it.
- It **returns immediately** when called from inside a round, effect, or
  output flush that is still running, or from a task one of those started
  (`_enclosing_run` ContextVar holds the owning task; tasks inherit it). That
  run may be waiting on the caller, so waiting could deadlock. Dependents still
  run in the next round, but code after the call can't rely on it. A task that
  outlives the effect that started it (an `ExtendedTask` body) waits normally.
- `run_next_round()` runs a round itself if none is running, else registers a
  `_next_round_waiters` future and sets `_rerun_round`. `ExtendedTask` uses it.
- Dispatch (`makeRequest`) tasks and `invalidate_later` timer tasks are *not*
  in `_tasks`, so `flush()` doesn't wait on them (a self-rearming timer would
  never let it return).
- A cross-thread `request_round()` is invisible to `run_until_idle()` until the
  loop runs the re-posted request.

## Async calcs and effects

- Everything is async inside the engine: `_utils.wrap_async` wraps sync
  functions. Each effect run is its own task, so **async effects interleave at
  every `await`**, within a session and across sessions. A sync effect still
  blocks the loop (and every session) while it runs. `ExtendedTask` is the way
  to run long work without holding the session busy.
- **Runs of one effect don't overlap** (unlike R): `on_flush_cb` awaits the
  previous run's `_run_done` future (shielded) before running. It then awaits
  the session's restore gate if any (`session._restore_gate(queued_priority)`,
  skipped once destroyed); see
  [bookmarking.md](bookmarking.md#restore-flow).
- `Effect_._run` runs inside `session_context(session)` and
  `use_otel_span(session._otel_reactive_update_span())`, then `await
  asyncio.sleep(0)` after the user function (issue #1381).
- **Concurrent calc readers share one run.** If an async calc is `_running` in
  another task (`_running_task`) and not invalidated, readers wait on
  `_run_waiters` instead of starting a second run. A nested run (the calc
  reading itself in the same task) is tracked with `_run_depth`; only the
  outermost run writes the cache.
- **Superseded runs are ignored.** Each run captures `run_id =
  _most_recent_ctx_id`; its `on_invalidate` and cache write only apply if it is
  still the latest run. A run cancelled before finishing caches nothing and
  sets `_invalidated = True`, so the next (or waiting) reader recomputes.
- A sync `Calc_.__call__` drives `get_value()` through `run_coro_sync`. If
  anything in the chain really yields (for example a sync calc that calls an
  async calc), it raises `RuntimeError("async function yielded control...")`.
  `CalcAsync_.__call__` is `async` and must be awaited.

## Effect destroy and cancellation

- `Effect_.destroy()` is idempotent (a session registers it for both end and
  destroy; a second cancel would interrupt cleanup). It sets `_destroyed`,
  cancels every task in `_run_tasks` (the running run and a re-run waiting on
  it) **except** `_enclosing_run.get()`, i.e. the run that called destroy
  directly or via a child task, then invalidates its context. That keeps an
  effect that destroys itself, or closes its own session, running to the end.
- `CancelledError` is delivered at the run's current `await` on the next loop
  pass, so `finally` blocks run after the `on_ended` / `on_destroy` callbacks
  (unless one of those awaits).
- Effects register their destroy with `session._on_destroy_first()`
  (`AsyncCallbacks.register(..., first=True)`), so within one scope they are
  cancelled before any other destroy callback, including an async one that
  could yield to a running effect after values are gone. Child scopes are
  still destroyed before their parent.
- Errors from a destroyed effect (e.g. cleanup reading a destroyed value, or
  `NotifyException(close=True)`) are printed but never close the session.

## `reactive.lock()` (deprecated)

- `lock()` warns once per process (`ShinyDeprecationWarning`, via a deferred
  import of `warn_deprecated`) and returns a `_NoOpLock`, an `asyncio.Lock`
  subclass that never blocks. Shiny itself takes no lock anywhere. To change
  state from a background task, call `value.set()` directly (it requests a
  round); use `session.run_once_when_idle()` to apply it between cycles.

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

- `invalidate_later(delay)` needs a current context. It starts a task
  (strong-referenced in `_timer_tasks`, not `_tasks`) that sleeps until a
  monotonic deadline, then sets `cancellable=False` and calls
  `session.run_once_when_idle(ctx.invalidate)`, so the invalidation is a
  cycle start action like an input change; without a session it calls
  `ctx.invalidate()` directly. The task is cancelled if the context is invalidated earlier or the
  session ends (`session.on_ended`).
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
  (`_done_tasks`; the event loop only keeps weak references). That task sets
  `status`/`value`/`error`, awaits `_reactive_environment.run_next_round()` so
  dependents *start* with this result before the next invocation replaces it
  (it doesn't wait for their async parts), then pops the next queued call.
- `cancel()` clears the queue and cancels the running task. The status then
  becomes `cancelled` through `_done_callback`.
- `result()`: `success` returns the value and `error` re-raises the error.
  `running` raises `req(False, cancel_output="progress")`
  (`SilentOperationInProgressException`); the output keeps its old value and
  shows progress. `initial` and `cancelled` raise a plain `SilentException`.
- Sessions: an ExtendedTask has **no `on_ended` hook** and is not cancelled
  at session end (as in R), so a running task keeps going after the session
  closes; call `task.cancel()` from `session.on_ended` to stop it. Its `Value`s survive session close
  on purpose (see Teardown) so the late completion doesn't hit
  `DestroyedReactiveError`.

## Error propagation

| Raised in an `Effect_` | Handling in `Effect_._run` |
| --- | --- |
| `SilentException` (+ `SilentOperationInProgressException` subclass) | swallowed |
| `NotifyException` | `notification_show` (sanitized if `e.sanitize`); `session._unhandled_error` if `e.close` and not destroyed |
| any other `Exception` | `ReactiveWarning`, then `session._unhandled_error` → `session.close()` (skipped once destroyed) |

- An exception that escapes `_run` inside the effect's task (`on_flush_cb`,
  e.g. from the restore gate) prints its traceback and goes to
  `session._unhandled_error`; with no session it is re-raised and
  `ReactiveEnvironment._on_task_done` prints it. `_unhandled_error` prints
  only the message, so callers print the traceback first.
- `Calc_._update_value` catches `Exception`, including silent ones, and
  **caches it** in `_error`. Every reader re-raises it until the calc is invalidated.
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
  cache. `Effect_.destroy()` cancels in-progress runs (see Effect destroy and
  cancellation). After that, `input._destroy()` and `output._destroy()` run.
- A destroyed effect can still have a pending queue entry: `on_flush_cb`
  skips `_run()` but still decrements the busy count.

## Pitfalls

- **`Value.set` compares by identity (`is`), not equality.** Setting an equal
  but different object invalidates dependents. Mutating an object in place
  and setting it again does **nothing**; assign a new object instead.
- `Value.unset()`'s docstring says it returns a bool, but it returns `None`.
  `freeze()` unsets the value *without* invalidating dependents.
- **Async effects interleave.** Two async effects (or outputs) of one session
  run concurrently, switching at each `await`. Shared mutable state, or
  per-render state stored on an object rather than in a `ContextVar`, can be
  clobbered by another run (see `_current_output_name` in
  [sessionMessaging.md](sessionMessaging.md#cycles-and-the-output-flush)).
  Inputs and timers are stable within a cycle; values set by other code are not.
- `reactive.lock()` no longer gives mutual exclusion. Code that used it as a
  mutex needs its own `asyncio.Lock`. `set()` returns before dependents run,
  unlike `lock()` + `await flush()`; keep `await reactive.flush()` if the code
  after relies on them.
- `await reactive.flush()` from inside an effect or flush callback returns
  immediately (see above); never use it to wait for dependents there.
- Don't swallow `CancelledError` in effects; cleanup goes in `finally`. A
  cancelled run's cleanup may read values its destroyed scope already tore
  down.
- Duck-typed session mocks (e.g. `OnEndedSessionCallbacks` in
  `tests/pytest/test_poll.py`) must implement `_on_destroy_first()`,
  `run_once_when_idle()`, `_increment_busy_count()`/`_decrement_busy_count()`,
  `_otel_reactive_update_span()`, and `_restore_gate()`, which `Effect_` and
  `invalidate_later` call.
- `SilentCancelOutputException` (and `SilentOperationInProgressException`)
  subclass `SilentException`, so an `except SilentException` also catches
  them. Where they need different handling (output observers), catch the
  subclasses first.
- When an `Effect_` is created under a stub session (Express UI pass), its
  `__init__` returns early, so the object is half-built and never runs.
- `asyncio.create_task` copies `ContextVar`s, so a task started inside an
  effect still sees that effect's (possibly invalidated) context as current.
  Reactive reads there silently attach to it, or fire immediately. Read
  values before spawning, or use `ExtendedTask`.
- A round only starts when a loop is running: invalidations made with no
  running loop request nothing, so code building a graph synchronously must
  run a round itself. In async tests, rounds start on the next loop pass;
  `await reactive.flush()` waits until idle.
- `reactive.flush()` waits on every session in the process, so a timer or
  long async effect elsewhere can delay a test's `flush()` indefinitely.
