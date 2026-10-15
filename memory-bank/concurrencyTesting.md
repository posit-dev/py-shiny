---
title: "Concurrency Testing"
description: "How to write in-process tests of sessions, rounds, cycles, and async effects in the style of tests/pytest/test_concurrency.py: Client drivers over MockConnection, wait_until with the 10 s limit, asyncio Events instead of sleeps for ordering, state waits plus settle() for negative assertions, duck-typed session mocks, MockTime, cleaning up tasks stranded on dead event loops, and how to run the suite. Read before adding or changing a test of reactive or session concurrency."
---

# Concurrency Testing

`tests/pytest/test_concurrency.py` tests the concurrency model described in
[reactiveInternals.md](reactiveInternals.md) and
[sessionMessaging.md](sessionMessaging.md): rounds that don't wait for async
effects, per-session cycles, output flushes, cancellation on destroy,
`run_once_when_idle()`, and the bookmark restore gate. The same patterns are
used in `tests/pytest/test_otel_reactive_update.py` (see
[otel.md](otel.md#testing)). CI is slow and noisy, so these tests never let a
timed sleep decide a result.

## Driving sessions

- `Client(server)` builds a real `AppSession` with
  `App(ui.TagList(), server)._create_session(MockConnection())` and runs
  `session._run()` as a task. `send()` / `update(**data)` feed JSON through
  `conn.cause_receive`; `close()` calls `cause_disconnect()` and awaits the
  task with `TIMEOUT`. Start a session with
  `c.send({"method": "init", "data": {...}})`; pass
  `".clientdata_output_<id>_hidden": False` for outputs that must render.
- Subclasses record what is sent: `RecordingClient` (`RecordingConnection`
  keeps `sent` and the busy count at each output send; takes
  `bookmark_store=`), `GatedClient` (`GatedConnection` can hold output sends
  open with `gate` or make them fail), and `RestoringClient` (inits from a
  bookmark URL).
- Helpers: `started_up(c)` waits for `_output_flush_enabled`, then
  `reactive.flush()`; `started(*clients)` inits and waits for the first input
  message; `in_thread(fn)` runs `fn` on another thread (hand reactive writes
  to the loop with `loop.call_soon_threadsafe`).
- Close every client in `finally`, and release any `Event` an effect waits
  on there too: sessions and `_reactive_environment` are shared by every test
  in an xdist worker.
- Tests of the bare engine use a local `ReactiveEnvironment()` or session-less
  `reactive.effect(...)` plus `await reactive.flush()`, and `destroy()` the
  effect at the end.

## Waiting without timing

- **`wait_until(cond)`** polls every 10 ms up to `TIMEOUT = 10.0` and returns
  a bool, so write `assert await wait_until(...)`. Wrap other awaits in
  `asyncio.wait_for(..., TIMEOUT)`. The limit is long on purpose: a passing
  wait returns immediately, and a busy worker can stall for over a second
  (e.g. the first `reactive.value()`'s name inference in `inspect.stack()`).
- **Order with `asyncio.Event`s, not sleep durations.** Have each step set a
  `started` event and wait on its own `release` event, then drive the order
  from the test (see `test_async_calc_reader_waits_for_the_latest_run`,
  `slow_effect(log, release)`). Remaining `asyncio.sleep()` calls only make a
  body async; no assertion may depend on their length.
- **Negative assertions ("X hasn't happened yet")** first wait for internal
  state proving X is parked, then run `settle()` (10 `asyncio.sleep(0)`
  passes) and assert. State to wait on: `session._cycle_start_action_queue`
  (a queued input update), `effect._run_tasks` (a run started or parked),
  `calc._run_waiters` (a reader waiting on a run), `session._busy_count`,
  `session._otel_cycle_span`. `at_restore_gate(effects, n)` is the restore
  gate version.
- `reactive.flush()` is a valid "everything settled" wait from test code, and
  fails fast through `wait_for` if a round loop never goes idle. It returns
  immediately when called from inside a flush.

## Session mocks and MockTime

- A duck-typed session (e.g. `OnEndedSessionCallbacks` in `test_poll.py`)
  used with `Effect_` or `invalidate_later` must provide what they call:
  `_on_destroy_first`, `_send_message_sync`, `run_once_when_idle`,
  `_increment_busy_count` / `_decrement_busy_count`,
  `_otel_reactive_update_span()` and `_restore_gate()` (both may return
  `None`).
- `tests/pytest/mocktime.py`'s `MockTime` patches `time.monotonic` and
  `asyncio.sleep` (used by `test_poll.py`, `test_reactives.py`).
  `advance_time()` wakes each sleeper, then yields until
  `_reactive_environment` has no round requested, running, or queued. It
  can't call `reactive.flush()`: that would wait on effects that are in a
  mocked sleep only `advance_time()` can end.

## Dead event loops and stranded tasks

A test that runs a loop of its own (`asyncio.new_event_loop()`,
`asyncio.run()`) and leaves tasks pending must release them inside the
test (see `test_round_state_from_a_dead_event_loop_is_discarded`):

- Park stranded tasks on a future that nothing else references
  (`loop.create_future()`), not an `Event` held in a local, so cleanup can
  collect them.
- Before returning, clear the environment's references
  (`env._abandoned_tasks.clear()`) and `gc.collect()` under
  `warnings.catch_warnings()` ignoring `RuntimeWarning`.

Otherwise the GC finalizes them in whichever test runs next: "coroutine ...
was never awaited" fails that test under `filterwarnings = error`, and on
Python 3.10/3.11 a "Task was destroyed" log during an import has failed an
unrelated test with an importlib `KeyError`.

## Running

- `.venv/bin/python -m pytest tests/pytest/test_concurrency.py -q`; the
  suite runs under xdist (`--numprocesses auto`), so run a new timing-sensitive
  test several times in parallel before trusting it.
- Never add `-p no:rerunfailures` (see
  [ciAndTooling.md](ciAndTooling.md#pytest-configuration)): it makes
  `test_utils.py` fail to collect and silently drops its tests.
- A hung test is killed after 120 s (`pytest.ini` `timeout`), with a
  faulthandler stack dump at 110 s.
