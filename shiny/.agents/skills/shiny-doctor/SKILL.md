---
name: shiny-doctor
description: "Auditing, diagnosing, validating, and debugging Shiny for Python (py-shiny) applications. Use when an app throws reactive errors, fails silently, has missing or duplicate UI/server IDs, exhibits reactive dependency cycles, leaks state across sessions, confuses Express and Core paradigms, mixes in R Shiny syntax, blocks the async event loop with synchronous I/O or incorrect extended_task usage, or when requested to validate, check, lint, debug, or doctor a Shiny app ('/shiny-doctor', 'shiny validate', 'diagnose my shiny app', 'why is my reactive not firing')."
---

# Shiny Doctor (`/shiny-doctor`)

Shiny Doctor is a diagnostic and validation engine for Shiny for Python applications. It audits reactive graph architecture, concurrency health, UI/server bindings, session isolation, framework idioms, and performs runtime verification.

When diagnosing an application, follow the **7-Phase Diagnostic Protocol** below to systematically inspect the codebase, reproduce issues, apply verified fixes, and perform runtime validation.

---

## Quick Diagnostic Checklist

| Category | Check | Common Symptom | Fix Reference |
|---|---|---|---|
| **Reactivity** | Side effects inside `@reactive.calc` | State instability, infinite reactive invalidation loops | [Antipatterns: Reactive Side Effects](references/antipatterns.md#1-side-effects-in-reactivecalc) |
| **Reactivity** | Missing call parentheses on reactive values/calcs (`count` instead of `count()`) | Silent failure or `<function ...>` rendered in UI | [Antipatterns: Uncalled Reactives](references/antipatterns.md#2-uncalled-reactive-functions) |
| **Reactivity** | Reading reactives outside reactive context | `SilentException` or crash outside server/effect | [Antipatterns: Missing Context](references/antipatterns.md#3-reading-reactives-outside-reactive-context) |
| **Reactivity** | Mutable object mutated in-place inside `reactive.value` | Graph fails to invalidate on change | [Antipatterns: In-Place Mutation](references/antipatterns.md#4-in-place-mutation-of-reactive-values) |
| **Reactivity** | Global `reactive.value` shared across all users | Session cross-talk / multi-user state leakage | [Antipatterns: Shared Global State](references/antipatterns.md#5-global-state-leakage-across-sessions) |
| **Async / Concurrency** | Synchronous blocking I/O or `time.sleep` in server or raw `extended_task` | Event loop freezes; app stops responding for all sessions | [Antipatterns: Blocking Event Loop](references/antipatterns.md#6-blocking-the-async-event-loop-and-extended-tasks) |
| **UI / Server Contract** | Mismatched ID between UI placeholder and server renderer | Output never displays / remains blank | [Antipatterns: ID Mismatch](references/antipatterns.md#7-mismatched-ui-and-server-ids) |
| **UI / Server Contract** | Duplicate input/output IDs in single namespace | Unpredictable input collisions and overrides | [Antipatterns: Duplicate IDs](references/antipatterns.md#8-duplicate-element-ids) |
| **Modules** | Mismatched UI/Server module instance IDs or duplicate module IDs | Module outputs disconnected; state collisions | [Antipatterns: Module Instance IDs](references/antipatterns.md#9-module-instance-id-mismatches-and-collisions) |
| **Paradigms** | Mixing Express syntax inside Core or creating `App()` in Express | Duplicate app initialization / layout breaks | [Antipatterns: Paradigm Mixing](references/antipatterns.md#10-mixing-express-and-core-paradigms) |
| **R Shiny Idioms** | Using `shinyApp`, `fluidPage`, `reactiveVal`, `observeEvent` | `NameError` or `ImportError` on startup | [Antipatterns: R Idioms](references/antipatterns.md#11-r-shiny-syntax-leakage) |

---

## Systematic 7-Phase Diagnostic Protocol

Execute these 7 inspection phases when diagnosing a Shiny app:

### Phase 1: Mode & Architecture Detection
1. **Identify Mode**:
   - **Express Mode**: Identified by `from shiny.express import ...` (e.g. `ui.page_opts()`, top-level UI declarations). Must **not** instantiate `app = App(app_ui, server)`.
   - **Core Mode**: Identified by `app_ui = ui.page_*()` and `def server(input, output, session):`, initialized with `app = App(app_ui, server)`.
2. **Verify Module Encapsulation**:
   - Core modules use `@module.ui` (which **automatically namespaces** all inner component IDs to the instance ID) and `@module.server`.
   - Verify that the module instance ID passed when invoking the UI (`my_module_ui("inst_1")`) exactly matches the instance ID passed to the server (`my_module_server("inst_1")`).
   - Ensure module instance IDs are unique within their calling scope.
   - Express modules use the `@module` decorator on the module function.

### Phase 2: Reactive Graph & Purity Audit
1. **Pure Calculations vs Side Effects**:
   - `@reactive.calc` must be pure and memoized: return derived computations without mutating state (`.set()`), writing to disk, or triggering external requests.
   - Use `@reactive.effect` (paired with `@reactive.event` when triggered by specific actions) for side effects.
2. **Calling Syntax**:
   - Verify that reactive values (`val()`) and calculations (`calc_fn()`) are invoked with parentheses `()` whenever their value is read.
3. **Dependency Isolation**:
   - Use `with reactive.isolate():` when reading a reactive value whose changes should *not* invalidate the caller.

### Phase 3: Concurrency & Async Health
1. **Event Loop Non-Blocking Rule**:
   - Server callbacks and reactive expressions execute on Python's asyncio event loop thread.
   - Synchronous blocking calls (`time.sleep()`, synchronous `requests.get()`, heavy synchronous DB queries) block the entire process and freeze all connected sessions.
   - Use native async calls (`await asyncio.sleep()`, `httpx.AsyncClient()`) for non-blocking I/O.
2. **Proper `@reactive.extended_task` Usage**:
   - `@reactive.extended_task` runs an asyncio task concurrently on the event loop thread using `asyncio.create_task`.
   - **Crucial**: Simply wrapping a synchronous `time.sleep()` or CPU-bound function inside an `async def` `@reactive.extended_task` **still blocks the event loop thread**.
   - For synchronous blocking I/O, offload to a worker thread: `await asyncio.to_thread(blocking_io_function, *args)`.
   - For heavy CPU-bound computation, offload to a process pool via `loop.run_in_executor(process_pool, cpu_bound_func, *args)`.

### Phase 4: UI / Server Contract & ID Consistency
1. **ID Matching**:
   - In Core mode, verify every `@render.xxx` function name matches an existing `ui.output_xxx("name")` ID.
   - Verify every `input.xxx()` read matches a declared `ui.input_xxx("xxx")` ID.
2. **ID Uniqueness**:
   - Ensure all input and output IDs are unique within their namespace.

### Phase 5: Session Isolation & State Scope
1. **Per-Session State**:
   - `reactive.value()`, user session data, and connection state must be created *inside* the `server()` function or module server (in Core) or inside the per-session execution context (in Express).
   - Never declare mutable `reactive.value()` objects at module/global scope.
2. **Container Mutation**:
   - When modifying lists or dictionaries in a `reactive.value`, re-assign a new/copied container or call `.set()` so downstream reactives invalidate properly.

### Phase 6: Observability & Performance
1. **Computation Caching**:
   - Cache expensive intermediate queries or transformations with `@reactive.calc` instead of recomputing inside multiple renderers.
2. **Telemetry Tracing**:
   - When diagnosing performance bottlenecks, use `shiny.otel` (`SHINY_OTEL_COLLECT=all`) to trace span timings across the reactive graph.

### Phase 7: Runtime Verification & Validation
1. **Server Startup Validation**:
   - When execution is available, start the application using `shiny run app.py` to verify application import and ASGI server startup without top-level syntax errors, import failures, or invalid schema configurations. (Do not rely on `python app.py`, which only executes top-level module code and exits without booting the Shiny server).
2. **Session-Level Verification**:
   - To claim full session-level runtime verification, connect to the application through a browser, Playwright harness, or Shiny test session (`shiny.test`) so that the `server(input, output, session)` function, reactive graph initialization, WebSocket connection, and `@render.*` outputs are genuinely exercised.
3. **Strict Verification Labeling Rule**:
   - **Never** claim an app's behavior is fully verified based purely on static code inspection or server port listening alone.
   - If connected client tests (e.g. Playwright or Shiny test sessions) passed, label as **Runtime Verified (Session Level)**.
   - If only server startup was executed without a client connection, label as **Server Startup Verified**.
   - If runtime execution was unavailable, explicitly label the diagnosis as **Static Diagnosis Only**.

---

## Detailed References
- [Antipatterns & Prescriptions Catalog](references/antipatterns.md)
- [Diagnostic Checklist & Verification Guide](references/diagnostics-checklist.md)
