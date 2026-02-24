# Concurrency Implementation Notes

Notes on deviations, surprises, and lessons learned while implementing `CONCURRENCY_PLAN.md`.

## Deviations from the Plan

### Phase ordering was collapsed

The plan proposed five sequential phases. In practice, Phases 1-4 were tightly coupled and implemented together in a single pass. The per-session lock (Phase 1) only makes sense once the `_run()` loop is restructured (Phase 4), and the cycle start action queue (Phase 3) is needed by the restructured `_run()` loop. Implementing them separately would have required intermediate states that were never actually correct.

### `lock()` returns a no-op instead of raising

The plan proposed making `lock()` raise a `RuntimeError`. We instead made it return a no-op lock object with a deprecation warning. This is less disruptive for any third-party code that might be calling `reactive.lock()`, and the deprecation warning makes the migration path clear. The `_NoOpLock` class implements the same interface as `asyncio.Lock` (including `__aenter__`/`__aexit__`) so `async with lock():` still works—it just doesn't do anything.

### `_cycle_start_action_queue` is a plain list, not `asyncio.Queue`

The plan proposed using `asyncio.Queue`. A plain `list` turned out to be simpler and sufficient, since the queue is only accessed from the session's own coroutine context (never from multiple concurrent producers). Using `list.append()` and `list.pop(0)` is straightforward and avoids the `await` overhead of `asyncio.Queue.get()`.

### `ExtendedTask` lost its lock entirely (not switched to per-session)

The plan didn't specifically address `ExtendedTask`, but it used the global `lock()`. Rather than threading a session reference into `ExtendedTask`, we simply removed the lock from its `_done_callback`. This works because:

- `ExtendedTask` only mutates its own `Value` objects (`status`, `value`, `error`)
- Those `Value.set()` calls trigger invalidation, which schedules effects on whatever session owns them
- The per-session lock protects the flush that actually runs those effects

There's no concurrent mutation risk because the done callback runs in a single `asyncio.create_task`, and Value.set() is synchronous.

### No configuration options added yet

The plan suggested adding `concurrent_effects` and `defer_inputs` options to `App()`. We deferred this—the concurrent behavior is now the only behavior. If we need a sequential fallback, `_flush_sequential()` is still available in the codebase and could be wired up behind a flag later.

## Unexpected Trickiness

### Concurrent flush needs an outer loop

The initial `_flush_concurrent()` implementation collected all pending contexts and ran them with `asyncio.gather()` once. This broke tests like `test_flush_runs_newly_invalidated` where Effect A mutates a Value that Effect B depends on. With sequential flush, B gets re-queued and re-run in the same `flush()` call because the `while not empty` loop picks it up. With a single gather, newly-invalidated effects were lost.

**Fix:** Wrapped the gather in an outer `while not self._pending_flush_queue.empty()` loop. Each iteration runs all currently-pending effects concurrently; if any of them invalidate new effects, those appear in the queue and get picked up in the next iteration.

### `invalidate_later` and mock sessions

`invalidate_later` was updated to use the session's per-session lock via `_cycle_start_action()`. But the poll tests use a minimal `OnEndedSessionCallbacks` mock that doesn't have `root_scope()`. Calling `session.root_scope()` on it raised `AttributeError`.

**Fix:** Wrapped the `root_scope()` call in a `try/except (AttributeError, TypeError)` and fell back to direct invalidation (no lock, no cycle queue) for non-`AppSession` objects. This is safe because mock/test sessions don't have concurrent message processing anyway.

### `on_flush_cb` needed try/finally for busy count

The original `on_flush_cb` in `Effect_._create_context()` decremented the busy count *after* the effect ran, but not in a `finally` block. If `_run()` raised an unexpected exception (caught by `gather`'s `return_exceptions=True`), the busy count would never decrement, permanently blocking the cycle start action queue.

**Fix:** Wrapped the body in `try/finally` so `_decrement_busy_count()` always executes.

### Default parameter trick for closures in loops

In `_run()`, the `process_update` and `process_dispatch` closures are defined inside a loop. Python's late-binding closures would cause all iterations to capture the *last* value of `message_data` or `message_other`. We used the default-parameter trick (`_data: dict[str, object] = message_data`) to capture the current value at definition time.

### `asyncio.sleep(0)` yield points determine interleaving order

The `test_async_sequential` test verified exact execution order of interleaved async effects. With concurrent flush, the order changed from sequential (`o1` fully completes, then `o2`) to interleaved (`o1` and `o2` alternate at each `await asyncio.sleep(0)` yield point). The interleaving is deterministic because CPython's event loop processes callbacks in FIFO order, so the test was updated with the new expected order rather than relaxed to be order-independent.

## Post-implementation review against R Shiny source

After the initial implementation, we did a detailed comparison against the R Shiny source (`R/shiny.R`, `R/server.R`, `R/reactives.R`). Two issues were found and fixed:

### `_start_cycle` needed a `_busy_count == 0` re-check

R Shiny double-checks `busyCount == 0` before executing in both `decrementBusyCount`'s `later()` callback and `startCycle`'s `on.exit`. This guards against the window between scheduling (`later()` / `create_task`) and execution, during which new effects may have been invalidated and incremented `busyCount`. Our initial `_start_cycle` only checked that the queue was non-empty. Added `if self._busy_count != 0: return` at the top.

### Dispatch messages should not be queued

R Shiny's message handler only defers `manageInputs` (input updates) through `cycleStartAction`. The `dispatch` fallthrough (for messages with `tag`/`args`, like `uploadEnd`, `makeRequest`) runs immediately. Our initial implementation queued both `update` and dispatch through `_cycle_start_action`, which would add unnecessary latency to features like `ExtendedTask` invocations and data frame cell edits. Fixed dispatch to run immediately under the session lock, matching R Shiny.

### Known remaining differences from R Shiny (deferred)

**`_request_flush()` removed entirely:** R Shiny calls `self$requestFlush()` in several places (including `decrementBusyCount`) to register the session into a global `appsNeedingFlush` map, which is then drained by the event loop's `serviceApp()`. In py-shiny, each session has its own message loop that calls `reactive_flush()` directly — there's no global "sessions needing flush" registry. The old `_request_flush()` / `App._request_flush()` was already a no-op with a TODO comment. We removed it and all call sites rather than perpetuating dead code.

**Output flushing granularity:** R Shiny's event loop calls `flushReact()` + `flushPendingSessions()` on every iteration of `serviceApp()`, so outputs from fast-completing effects are sent to the client even while slow effects are still running. Our `_flush_concurrent()` uses `asyncio.gather()`, which waits for *all* effects in a batch before `_flushed_callbacks` fires and output messages are sent. This is a responsiveness difference (not correctness); fixing it would require replacing `gather` with something like `asyncio.TaskGroup` + incremental output flushing.

## What Wasn't Changed

- **`ReactiveEnvironment` remains a global singleton.** The plan's per-session lock is on `AppSession`, not on `ReactiveEnvironment`. The reactive environment's pending flush queue is still global, which means `flush()` runs all pending effects across all sessions. This is fine because effects from different sessions don't share state (beyond the global queue itself), and the per-session lock prevents concurrent message processing within a session.

- **`SessionProxy` delegates to root.** `_increment_busy_count`, `_decrement_busy_count`, and all the new cycle management methods live on `AppSession`. `SessionProxy` already delegates these calls to the root session, so modules work correctly without changes.

- **File uploads and downloads.** `_handle_request` already had its own `_increment_busy_count`/`_decrement_busy_count` pair. No changes needed. Downloads run in an isolated context and don't interact with the reactive flush cycle.
