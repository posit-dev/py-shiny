# Shiny Doctor: app audit and repair

Shiny Doctor is a diagnostic and repair engine for Shiny for Python applications. It audits reactive graph architecture, concurrency health, UI/server bindings, session isolation, and framework idioms.

## Quick Diagnostic Index

**Do NOT read large reference documents upfront.** Inspect the target app's code and tests first, match symptoms to the table below, and consult [Antipatterns Catalog](antipatterns.md) only for specific unfamiliar sections.

| Symptom / Observed Issue | Likely Root Cause | Prescription | Antipattern Reference |
|---|---|---|---|
| Blank output or unpopulated UI area | Mismatched output ID between UI and server | Match each renderer's effective ID to its UI placeholder, including within modules. | Section 7 |
| Output shows `<function ... at 0x...>` | Uncalled reactive value or calculation | Add parentheses when reading: call `val()` not `val`. | Section 2 |
| State leaks between browser sessions or across users | State declared at module/global scope | In Core, move state inside `server()`. In Express, declare state in `app.py`'s per-session scope, not imported modules. | Section 5 |
| UI/server freezes during long task; clicks/pings blocked | Synchronous blocking I/O or CPU work in async loop | Use `@reactive.extended_task` with `asyncio.to_thread` (I/O) or `ProcessPoolExecutor` (CPU). Pass reactive values as parameters; do not read reactives inside the task. | Section 6 |
| Updates trigger without user action, or infinite loop | Side effects inside `@reactive.calc` or an action effect running at startup | Keep `@reactive.calc` pure. Gate action effects with `@reactive.event(...)`; check initial button values and `ignore_none` / `ignore_init`. | Section 1 |
| Mutating list or dict fails to trigger downstream updates | In-place collection mutation | Create and set a new copy: `val.set(val() + [item])` or `val.set({**val(), k: v})`. | Section 4 |
| `RuntimeError: No current reactive context` | Reading reactive outside calc/effect/render | Wrap reading in a calculation, effect, or render function. | Section 3 |
| Module outputs blank or collisions between instances | Namespace ID mismatch | Ensure `mod_ui("id")` and `mod_server("id")` use identical instance IDs. | Section 9 |
| Duplicate element IDs warning or unexpected overrides | Duplicate ID across UI components | Ensure every input/output ID is unique within its namespace. | Section 8 |
| `App(app_ui, server)` in Express or mode syntax collision | Mixing Express and Core paradigms | Express uses top-level UI components directly without `App(...)`. Core uses explicit `app = App(app_ui, server)`. | Section 10 |
| R Shiny syntax (`shinyApp`, `fluidPage`, `observeEvent`) | R Shiny idioms copied to Python | Use Python equivalents (`ui.page_fluid`, `@reactive.effect` + `@reactive.event`). | Section 11 |

---

## Diagnostic Workflow

1. **Static Inspection & Imports**: Read the app, README, and existing tests. Identify Core or Express mode and the public behavior and IDs to preserve. An import check can catch syntax errors but does not run a Shiny session.
2. **Identify Symptoms**: Match observed issues against the Quick Diagnostic Index above. Check for session leaks (global variables), event loop blocks (`time.sleep` or synchronous I/O in async server), and output ID mismatches.
3. **Targeted Fix**: Apply the precise pattern from the table. If you need full before/after code examples, read only the relevant section in [Antipatterns Catalog](antipatterns.md).
4. **Verification**: Use an existing connected browser test with `shiny.pytest` fixtures, or start Shiny with a managed process, readiness timeout, and cleanup and connect a browser or Playwright client. Test the repaired behavior through the live session. For session-state or blocking-work bugs, exercise two sessions; while a slow task runs, check click-time inputs and another session's responsiveness. Preserve required service results and latency. A passing connected test also verifies startup, so a separate startup probe is unnecessary.

If Playwright fails with `EPERM` while resolving a symlinked Node driver, retry once with `NODE_OPTIONS='--preserve-symlinks-main --preserve-symlinks'` or a valid `PLAYWRIGHT_NODEJS_PATH`. Keep searches bounded: target app code first, restrict installed-package searches to relevant Python files, and exclude minified JavaScript and source maps. Rerun a passing focused suite only after a code change.

Report what ran. Use **Runtime Verified (Session Level)** only for passing connected tests, **Server Startup Verified** for startup alone, and **Static Diagnosis Only** when runtime execution was unavailable.

---

## References

- [Antipatterns Catalog](antipatterns.md): In-depth catalog of Shiny antipatterns with symptoms, bad vs. good code examples, and prescriptions.
- [Diagnostic Checklist](diagnostics-checklist.md): 7-phase audit checklist for architecture, reactivity, concurrency, and session scope.

## Shared Shiny References

After inspecting the app, read only the guides relevant to the diagnosis before
writing a repair. Use the antipatterns catalog for symptom-specific examples;
use these guides for framework APIs and verification techniques.

| Finding / Task | Reference |
|---|---|
| Reactive loops, stale values, event gating, or reactive context errors | [Reactivity](reactivity.md) |
| Blocking work or an unresponsive session | [Extended tasks](extended-tasks.md) |
| Express scope or mixed Core/Express syntax | [Express mode](express.md) |
| Module instance IDs or namespace collisions | [Core modules](modules-core.md) or [Express modules](modules-express.md), according to app mode |
| Per-session resources or cleanup | [Session lifecycle](session-lifecycle.md) |
| Inspect live inputs, outputs, or internal reactive values | [Debugging](debugging.md) |
| Verify a repair through connected browser sessions | [Playwright testing](testing.md) |
| Exercise server logic in memory | [Test server](test-server.md); this does not replace connected verification for UI, session-isolation, or responsiveness bugs |

Read the [Diagnostic Checklist](diagnostics-checklist.md) for a broad app audit;
for a specific bug, use only the relevant checks.
