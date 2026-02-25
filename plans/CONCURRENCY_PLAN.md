# Py-Shiny Concurrency Improvements: Implementation Plan

## Executive Summary

This document outlines a plan to implement R Shiny-style concurrency in py-shiny. Currently, py-shiny has two levels of serialization that prevent concurrent execution: a global reactive lock that serializes all sessions, and sequential effect execution within sessions. This plan proposes moving to a per-session concurrency model where sessions run independently, effects execute concurrently within a session, but input processing is deferred while effects are running to keep input values stable.

## Background: Current py-shiny Architecture

### Application Structure

Py-shiny is built on Starlette. The key files are:

1. **`shiny/_app.py:217`** - `App.init_starlette_app()` creates the Starlette application
   - WebSocket route at `/websocket/` connects to `_on_connect_cb` (line 388)
   - Each client connection creates an `AppSession` and launches its control loop

2. **`shiny/session/_session.py:599`** - `AppSession._run()` is the session control loop
   ```python
   async def _run(self) -> None:
       while True:
           message: str = await self._conn.receive()  # line 619
           # ... parse message ...
           async with lock():  # line 639 - THE GLOBAL LOCK
               # Process message (init, update, or dispatch)
               # ... handle message ...
               await reactive_flush()  # line 705
   ```

3. **`shiny/reactive/_core.py`** - Contains the reactive system
   - Line 199: `_reactive_environment = ReactiveEnvironment()` - a **single global instance**
   - Lines 135-147: The `ReactiveEnvironment` has a **single global `asyncio.Lock`**
   - Line 292: `lock()` function returns this global lock
   - Lines 175-185: `_flush_sequential()` runs effects sequentially

### Current Concurrency Behavior

**Problem 1: Global Serialization**
- All sessions share the same reactive lock
- When Session A processes a message (inside `async with lock():`), Sessions B, C, D must wait
- Long operations in one session block ALL other sessions

**Problem 2: Sequential Effect Execution**
From `shiny/reactive/_core.py:180-185`:
```python
async def _flush_sequential(self) -> None:
    # Sequential flush: instead of storing the tasks in a list and calling gather()
    # on them later, just run each effect in sequence.
    while not self._pending_flush_queue.empty():
        ctx = self._pending_flush_queue.get()
        await ctx.execute_flush_callbacks()
```

The comment explicitly mentions the alternative (using `gather()`), but the current implementation is sequential.

**Current State Summary:**
- ❌ Sessions cannot process messages concurrently
- ❌ Effects within a session run sequentially
- ❌ No mechanism to defer input processing during effect execution

## Background: R Shiny Concurrency Model

### Key Files in R Shiny Source

Located at `/Users/jcheng/Development/rstudio/shiny/`:

1. **`R/shiny.R:343`** - `ShinySession` R6 class definition
2. **`R/shiny.R:352`** - `cycleStartActionQueue` member variable
3. **`R/shiny.R:360`** - `busyCount` member variable
4. **`R/shiny.R:657`** - `startCycle()` method
5. **`R/shiny.R:1348`** - `cycleStartAction()` method
6. **`R/shiny.R:2194-2220`** - `incrementBusyCount()` and `decrementBusyCount()`
7. **`R/reactives.R:1192`** - Observer increments busy count on invalidation
8. **`R/reactives.R:1225`** - Observer decrements busy count in finally block

### How R Shiny Handles Concurrency

**Key Components:**

1. **`cycleStartActionQueue`** - A per-session queue (fastqueue)
   - Holds callbacks that need to execute at the "start of a cycle"
   - Most importantly: **input message processing is queued here**

2. **`busyCount`** - A per-session counter
   - Tracks how many observers are currently executing
   - Incremented when an observer is invalidated and scheduled
   - Decremented when an observer completes (in finally block)

3. **`cycleStartAction(callback)`** - Adds callback to the queue
   ```r
   cycleStartAction = function(callback) {
     private$cycleStartActionQueue$add(callback)
     if (private$busyCount == 0L) {
       private$startCycle()
     }
   }
   ```
   - If no observers running (`busyCount == 0`): immediately calls `startCycle()`
   - If observers are running (`busyCount > 0`): callback waits in queue

4. **`startCycle()`** - Processes one action from the queue
   ```r
   startCycle = function() {
     if (private$cycleStartActionQueue$size() > 0) {
       head <- private$cycleStartActionQueue$remove()

       on.exit({
         if (private$busyCount == 0L && private$cycleStartActionQueue$size() > 0L) {
           later::later(function() {
             if (private$busyCount == 0L) {
               private$startCycle()
             }
           })
         }
       }, add = TRUE)

       head()  # Execute the callback
     }
   }
   ```

5. **Input Processing** - From `R/shiny.R:2159`:
   ```r
   self$cycleStartAction(doManageInputs)
   ```
   New inputs from client are **not** processed immediately; they're enqueued.

6. **Observer Busy Tracking** - From `R/reactives.R`:
   ```r
   # When observer is invalidated (line 1192):
   .domain$incrementBusyCount()

   # In onFlush callback (line 1225):
   finally = .domain$decrementBusyCount
   ```

### R Shiny Concurrency Properties

- ✅ **Sessions are independent** - No global lock, each session has its own state
- ✅ **Observers run concurrently** - Multiple async observers can execute simultaneously within a session
- ✅ **Inputs are stable** - While `busyCount > 0`, new inputs are queued but not processed
- ✅ **Ordered processing** - Once all observers finish, queued actions execute in order

**Example Flow:**
1. User changes `input$x` → invalidates 3 observers → `busyCount = 3`
2. All 3 observers start executing concurrently (async)
3. While they run, user changes `input$y` → queued via `cycleStartAction()`, NOT processed yet
4. Observer 1 finishes → `busyCount = 2`
5. Observer 2 finishes → `busyCount = 1`
6. Observer 3 finishes → `busyCount = 0` → triggers `startCycle()`
7. Now `input$y` change is processed, invalidating observers with stable input state

## Motivation for Changes

### Why This Matters

1. **Scalability** - Currently, a single slow session blocks all other sessions on the same server
2. **Responsiveness** - Long-running calculations prevent other effects from starting
3. **Correctness** - Input values can change while async calculations are in progress, leading to inconsistent state
4. **Parity** - R Shiny users expect this behavior; py-shiny should match it

### Use Case Example

**Current behavior (problematic):**
```python
@reactive.effect
async def effect1():
    # Reads input.x
    await expensive_api_call()  # Takes 5 seconds
    # Uses input.x again - but it might have changed!

@reactive.effect
async def effect2():
    # Must wait for effect1 to complete before starting
    await another_task()
```

**Desired behavior:**
```python
@reactive.effect
async def effect1():
    # Reads input.x (busyCount = 1)
    await expensive_api_call()  # During this, input.x changes are queued
    # Uses input.x - guaranteed to be the same value

@reactive.effect
async def effect2():
    # Starts immediately, runs concurrently with effect1
    # Both effects see stable input values
    await another_task()
```

## Implementation Plan

### Phase 1: Per-Session Reactive Lock

**Goal:** Remove global lock, enable session concurrency

**Changes:**

1. **`shiny/reactive/_core.py`**
   ```python
   class ReactiveEnvironment:
       def __init__(self) -> None:
           # ... existing code ...
           # REMOVE: self._lock: Optional[asyncio.Lock] = None
           # REMOVE: The lock property (lines 135-147)

   # MODIFY the lock() function (line 292):
   def lock() -> asyncio.Lock:
       """
       DEPRECATED: This function is deprecated and will raise an error.
       Reactive locking is now handled per-session.
       """
       raise RuntimeError(
           "reactive.lock() is deprecated. The reactive lock is now per-session."
       )
   ```

2. **`shiny/session/_session.py`**
   ```python
   class AppSession(Session):
       def __init__(self, app: App, id: str, conn: Connection, debug: bool = False):
           # ... existing code ...

           # ADD: Per-session reactive lock
           self._reactive_lock: asyncio.Lock = asyncio.Lock()

       async def _run(self) -> None:
           # ... existing code ...
           while True:
               message: str = await self._conn.receive()
               # ... parse message ...

               # CHANGE: Use session lock instead of global lock
               async with self._reactive_lock:  # Changed from: async with lock()
                   # ... process message ...
                   await reactive_flush()
   ```

**Testing:**
- Create 2 sessions
- Have Session A process a slow message
- Verify Session B can process messages concurrently

### Phase 2: Concurrent Effect Execution

**Goal:** Allow effects to run concurrently within a session

**Changes:**

1. **`shiny/reactive/_core.py`** - Replace sequential flush with concurrent
   ```python
   class ReactiveEnvironment:
       async def flush(self) -> None:
           """Flush all pending operations"""
           await self._flush_concurrent()  # Changed from: _flush_sequential()
           await self._flushed_callbacks.invoke()

       async def _flush_concurrent(self) -> None:
           """Run all pending contexts concurrently using asyncio.gather()"""
           tasks = []
           while not self._pending_flush_queue.empty():
               ctx = self._pending_flush_queue.get()
               tasks.append(ctx.execute_flush_callbacks())

           if tasks:
               await asyncio.gather(*tasks, return_exceptions=True)

       # Keep _flush_sequential as an option for testing
       async def _flush_sequential(self) -> None:
           # ... existing implementation ...
   ```

2. **`shiny/reactive/_reactives.py`** - Update Effect to track busy state
   ```python
   class Effect_:
       def _create_context(self) -> Context:
           ctx = Context()
           self._ctx = ctx

           def on_invalidate_cb() -> None:
               self._ctx = None
               for cb in self._invalidate_callbacks:
                   cb()

               if self._destroyed:
                   return

               def _continue() -> None:
                   ctx.add_pending_flush(self._priority)
                   if self._session:
                       # ADD: Increment busy count when effect is scheduled
                       self._session._increment_busy_count()

               if self._suspended:
                   self._on_resume = _continue
               else:
                   _continue()

           async def on_flush_cb() -> None:
               try:
                   if not self._destroyed:
                       await self._run()
               finally:
                   # ADD: Always decrement in finally block
                   if self._session:
                       self._session._decrement_busy_count()

           ctx.on_invalidate(on_invalidate_cb)
           ctx.on_flush(on_flush_cb)
           return ctx
   ```

**Testing:**
- Create effects that log start/end times
- Verify effects run concurrently (overlapping time ranges)
- Verify busy indicator works correctly

### Phase 3: Cycle Start Action Queue

**Goal:** Implement the queue and busy counting infrastructure

**Changes:**

1. **`shiny/session/_session.py`** - Add queue and methods
   ```python
   class AppSession(Session):
       def __init__(self, app: App, id: str, conn: Connection, debug: bool = False):
           # ... existing code ...

           # ADD: Cycle start action queue
           self._cycle_start_action_queue: asyncio.Queue[Callable[[], Awaitable[None]]] = asyncio.Queue()

           # Note: _busy_count already exists at line 517, but currently only used for UI indicator
           # We'll now use it for queue management too

       async def cycle_start_action(self, callback: Callable[[], Awaitable[None]]) -> None:
           """
           Schedule an action to execute when no effects are busy.
           This is used to defer input processing until effects complete.
           """
           await self._cycle_start_action_queue.put(callback)

           # If no effects are running, start processing immediately
           if self._busy_count == 0:
               await self._start_cycle()

       async def _start_cycle(self) -> None:
           """
           Process one action from the cycle start queue.
           Called when busyCount reaches 0, or when an action is added to an empty queue.
           """
           if self._cycle_start_action_queue.empty():
               return

           # Get one action from the queue
           callback = await self._cycle_start_action_queue.get()

           # Execute it
           await callback()

           # After execution, if busyCount is still 0 and there are more actions,
           # schedule the next cycle (use asyncio.create_task to avoid deep recursion)
           if self._busy_count == 0 and not self._cycle_start_action_queue.empty():
               asyncio.create_task(self._start_cycle())

       def _increment_busy_count(self) -> None:
           # This already exists, but add documentation
           """
           Increment the busy count.
           Called when an effect is scheduled for execution.
           When count goes from 0 to 1, sends 'busy' message to client.
           """
           # ... existing implementation ...

       def _decrement_busy_count(self) -> None:
           # This already exists at line 1083, but needs modification
           """
           Decrement the busy count.
           When count reaches 0, sends 'idle' message and starts next cycle.
           """
           self._busy_count -= 1
           if self._busy_count == 0:
               self._send_message_sync({"busy": "idle"})
               # ADD: Start processing queued actions
               asyncio.create_task(self._start_cycle())
   ```

**Testing:**
- Enqueue multiple actions
- Verify they execute in order
- Verify execution is deferred when busy

### Phase 4: Defer Input Processing

**Goal:** Queue input messages instead of processing them immediately

**Changes:**

1. **`shiny/session/_session.py`** - Modify message loop
   ```python
   async def _run(self) -> None:
       conn_state: ConnectionState = ConnectionState.Start

       # ... existing setup code ...

       while True:
           message: str = await self._conn.receive()
           # ... parse message ...

           if message_obj["method"] == "init":
               # SPECIAL CASE: Init must run immediately to set up the session
               async with self._reactive_lock:
                   verify_state(ConnectionState.Start)
                   # ... existing init handling ...
                   conn_state = ConnectionState.Running

           elif message_obj["method"] == "update":
               # CHANGE: Queue input updates instead of processing immediately
               message_data = typing.cast(ClientMessageUpdate, message_obj)["data"]

               async def process_update():
                   async with self._reactive_lock:
                       verify_state(ConnectionState.Running)
                       self._manage_inputs(message_data)
                       await reactive_flush()

               await self.cycle_start_action(process_update)

           elif "tag" in message_obj and "args" in message_obj:
               # CHANGE: Queue message dispatch too
               message_other = typing.cast(ClientMessageOther, message_obj)

               async def process_dispatch():
                   async with self._reactive_lock:
                       verify_state(ConnectionState.Running)
                       await self._dispatch(message_other)
                       await reactive_flush()

               await self.cycle_start_action(process_dispatch)
   ```

**Key Points:**
- `init` message must run immediately (session setup)
- `update` messages (input changes) are queued
- Message handler dispatch is queued
- Each queued action acquires the lock, processes, and flushes

**Testing:**
- Trigger input change during slow effect
- Verify input change is queued
- Verify it processes after effect completes
- Verify input values are stable during effect execution

### Phase 5: Edge Cases and Testing

**Edge Cases to Handle:**

1. **`invalidate_later`** (from `shiny/reactive/_core.py:305`)
   - Already uses the lock correctly (line 362: `async with lock()`)
   - Needs to be updated to use session lock
   - Should probably use `cycle_start_action` to queue the invalidation

2. **Session Cleanup**
   - When session closes, cancel any queued cycle actions
   - Ensure busy count is reset
   - Add to `_run_session_ended_tasks()` method

3. **File Uploads** (`_handle_request` in _session.py:843)
   - Already increments/decrements busy count
   - Should continue to work correctly

4. **Downloads**
   - Currently run in isolation context
   - Should not affect busy counting
   - Verify this is correct

5. **`send_custom_message` and `send_input_message`**
   - These send messages to the client
   - Should NOT require queueing (they don't modify inputs)
   - Verify they work during busy periods

**Comprehensive Testing Plan:**

1. **Unit Tests:**
   - Test cycle_start_action queue ordering
   - Test busy count tracking
   - Test concurrent effect execution
   - Test lock acquisition/release

2. **Integration Tests:**
   - Multiple sessions with concurrent loads
   - Input stability during async effects
   - invalidate_later during busy periods
   - File upload/download during effects
   - Session termination with queued actions

3. **Performance Tests:**
   - Benchmark before/after changes
   - Test with many concurrent sessions
   - Test with many effects per session
   - Memory leak testing (ensure contexts are cleaned up)

4. **Stress Tests:**
   - Rapid input changes
   - Long-running effects (minutes)
   - Many short effects
   - Mixed workloads

## Migration Considerations

### Breaking Changes

1. **`reactive.lock()` function** - This will raise an error
   - **Impact:** Low - This is an advanced/undocumented feature
   - **Migration:** Users should not need the global lock anymore
   - If needed, they can use their own lock

2. **Effect execution order** - Effects will run concurrently, not sequentially
   - **Impact:** Medium - If users depend on execution order, this could break
   - **Migration:** Use priority parameter or explicit dependencies
   - Consider adding a global option to fall back to sequential execution

3. **Input timing** - Input changes are queued during effect execution
   - **Impact:** Low to Medium - This is actually the desired behavior
   - **Migration:** Most code should work better, but some edge cases might behave differently

### Compatibility Options

Consider adding configuration options:

```python
# In app.py or a new config module
app = App(
    ui,
    server,
    # New options:
    concurrent_effects=True,  # Default: True, set False for sequential
    defer_inputs=True,        # Default: True, set False for immediate processing
)
```

This allows gradual migration and easier debugging.

## Success Criteria

The implementation is successful when:

1. ✅ Multiple sessions can process messages concurrently
2. ✅ Effects within a session run concurrently
3. ✅ Input values remain stable during effect execution
4. ✅ All existing tests pass (or are updated appropriately)
5. ✅ Performance improves for multi-session scenarios
6. ✅ No memory leaks or resource issues
7. ✅ Behavior matches R Shiny's concurrency model

## References

- **Py-shiny repo:** `/Users/jcheng/Development/posit-dev/py-shiny4/`
- **R Shiny repo:** `/Users/jcheng/Development/rstudio/shiny/`
- Key R Shiny file: `R/shiny.R` (ShinySession class, cycle management)
- Key R Shiny file: `R/reactives.R` (Observer implementation, busy counting)
- Key py-shiny files:
  - `shiny/_app.py` (Starlette app setup)
  - `shiny/session/_session.py` (Session control loop)
  - `shiny/reactive/_core.py` (Reactive system core)
  - `shiny/reactive/_reactives.py` (Effect/Calc implementations)

## Timeline Estimate

- **Phase 1:** 2-3 days (per-session locks)
- **Phase 2:** 3-4 days (concurrent effects)
- **Phase 3:** 2-3 days (queue infrastructure)
- **Phase 4:** 2-3 days (defer input processing)
- **Phase 5:** 5-7 days (testing and edge cases)

**Total:** 14-20 days of development time

## Next Steps

1. Review this plan with the team
2. Set up a feature branch
3. Begin with Phase 1 (least invasive change)
4. Implement comprehensive tests alongside each phase
5. Consider feature flag for gradual rollout
6. Update documentation to explain concurrency model
