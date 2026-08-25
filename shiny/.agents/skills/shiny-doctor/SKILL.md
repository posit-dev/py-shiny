---
name: shiny-doctor
description: "Auditing, diagnosing, validating, and debugging Shiny for Python (py-shiny) applications. Use when an app throws reactive errors, fails silently, has missing or duplicate UI/server IDs, exhibits reactive dependency cycles, leaks state across sessions, confuses Express and Core paradigms, mixes in R Shiny syntax, blocks the async event loop with synchronous I/O, or when requested to validate, check, lint, debug, or doctor a Shiny app ('/shiny-doctor', 'shiny validate', 'diagnose my shiny app', 'why is my reactive not firing')."
---

# Shiny Doctor (`/shiny-doctor`)

Shiny Doctor is a diagnostic and validation engine for Shiny for Python applications. It audits reactive graph architecture, concurrency health, UI/server bindings, session isolation, and framework idioms.

When invoked with a target Shiny application or code snippet, follow the **Diagnostic Protocol** below to audit the code systematically, identify issues, and provide verified fixes.

---

## Quick Diagnostic Checklist

| Category | Check | Common Symptom | Fix Reference |
|---|---|---|---|
| **Reactivity** | Side effects inside `@reactive.calc` | State instability, infinite reactive loops | [Antipatterns: Reactive Side Effects](references/antipatterns.md#1-side-effects-in-reactivecalc) |
| **Reactivity** | Missing call parentheses on reactive values/calcs (`count` instead of `count()`) | Silent failure or `<function ...>` printed | [Antipatterns: Uncalled Reactives](references/antipatterns.md#2-uncalled-reactive-functions) |
| **Reactivity** | Reading reactives without a reactive context | `SilentException` or runtime crash outside server/effect | [Antipatterns: Missing Context](references/antipatterns.md#3-reading-reactives-outside-reactive-context) |
| **Reactivity** | Mutable object mutated in-place inside `reactive.value` | Graph fails to invalidate on change | [Antipatterns: In-Place Mutation](references/antipatterns.md#4-in-place-mutation-of-reactive-values) |
| **Reactivity** | Global `reactive.value` shared across all users | Session cross-talk / state leakage | [Antipatterns: Shared Global State](references/antipatterns.md#5-global-state-leakage-across-sessions) |
| **Async / Concurrency** | Synchronous blocking I/O or `time.sleep` in server function | Entire server freezes for all sessions | [Antipatterns: Blocking Event Loop](references/antipatterns.md#6-blocking-the-async-event-loop) |
| **UI / Server Contract** | Mismatched ID between UI placeholder and server renderer | Output never displays / remains blank | [Antipatterns: ID Mismatch](references/antipatterns.md#7-mismatched-ui-and-server-ids) |
| **UI / Server Contract** | Duplicate input/output IDs in single namespace | Unpredictable input overrides | [Antipatterns: Duplicate IDs](references/antipatterns.md#8-duplicate-element-ids) |
| **Modules** | Forgetting `ns()` in UI or missing `@module.server` | Module inputs/outputs disconnected | [Antipatterns: Module Namespacing](references/antipatterns.md#9-module-namespace-omission) |
| **Paradigms** | Mixing Express syntax inside Core or creating `App()` in Express | Duplicate app initialization / layout breaks | [Antipatterns: Paradigm Mixing](references/antipatterns.md#10-mixing-express-and-core-paradigms) |
| **R Shiny Idioms** | Using `shinyApp`, `fluidPage`, `reactiveVal`, `observeEvent` | `NameError` or `ImportError` on startup | [Antipatterns: R Idioms](references/antipatterns.md#11-r-shiny-syntax-leakage) |

---

## Systematic Diagnostic Protocol

Execute these 6 inspection phases when diagnosing a Shiny app:

### Phase 1: Mode & Architecture Detection
1. **Identify Mode**:
   - **Express Mode**: Identified by `from shiny.express import ...` (e.g. `ui.page_opts()`, top-level UI components). Must **not** define `app = App(app_ui, server)`.
   - **Core Mode**: Identified by `app_ui = ui.page_*()` and `def server(input, output, session):`, initialized with `app = App(app_ui, server)`.
2. **Verify Module Encapsulation**:
   - Core modules must define `@module.ui` with `ns = session.ns` (or `ns = Namespacer(id)`), and `@module.server` for server logic.
   - Express modules must use `@module` decorator on the module function.

### Phase 2: Reactive Graph & Purity Audit
1. **Pure Calculations vs Effects**:
   - `@reactive.calc` must be purely functional: compute and return a value derived from reactive sources without mutating external state, calling `.set()`, or triggering external I/O.
   - `@reactive.effect` must be used for side effects (writing to disk, updating external services, triggering UI updates).
2. **Explicit Triggers with `@reactive.event`**:
   - When an effect or calc should only re-evaluate on specific action button clicks or input changes, decorate with `@reactive.event(input.btn)`.
   - Ensure `ignore_none=True` / `ignore_init=True` are used where appropriate to prevent unwanted startup execution.
3. **Dependency Isolation**:
   - Use `with reactive.isolate():` when reading a reactive value or calculation whose changes should *not* cause the caller to invalidate.

### Phase 3: Concurrency & Async Health
1. **Event Loop Non-Blocking Rule**:
   - Server callbacks and reactive expressions run on Python's asyncio event loop.
   - Never use `time.sleep()`, synchronous `requests.get()`, or blocking DB drivers in reactive calculations or effects.
   - Use `await asyncio.sleep()`, `httpx.AsyncClient()`, or async database drivers.
2. **Long-Running Compute with Extended Tasks**:
   - For CPU-bound calculations or slow synchronous APIs, use `@reactive.extended_task` with `task.result()` and `ui.input_task_button` to keep the UI responsive without blocking other sessions.

### Phase 4: UI / Server Contract & ID Consistency
1. **ID Matching**:
   - Check that every `@render.xxx` function name in server matches the corresponding `ui.output_xxx("name")` in UI (Core mode).
   - Check that input IDs read in `input.xxx()` correspond to valid `ui.input_xxx("xxx")` declarations.
2. **No Collisions**:
   - All input and output IDs within the same namespace must be unique.

### Phase 5: Session Isolation & State Scope
1. **Per-Session State**:
   - `reactive.value()`, database connections, user preferences, and session data must be initialized *inside* the `server()` function or module server (in Core) or inside the per-session execution context (in Express).
   - Module-level / global variables must only be used for read-only immutable configuration or connection pools.

### Phase 6: Observability & Performance
1. **Efficient Computation**:
   - Avoid recalculating large datasets repeatedly; cache intermediate transformations with `@reactive.calc`.
   - Prefer vectorised or Narwhals / Polars / Pandas operations over Python row-level iteration.
2. **Tracing**:
   - Use `shiny.otel` (`export SHINY_OTEL_COLLECT=all`) to profile execution bottlenecks across reactive dependencies when investigating latency.

---

## Detailed References
- [Antipatterns & Prescriptions Catalog](references/antipatterns.md)
- [Diagnostic Checklist & Verification Guide](references/diagnostics-checklist.md)
