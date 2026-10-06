# Shiny Doctor Diagnostic Checklist

This reference provides a step-by-step audit and verification checklist for validating and diagnosing a Shiny for Python codebase.

---

## 1. Mode & Architecture Checklist
- [ ] Are imports using `shiny` or `shiny.express` consistently without cross-mode collisions?
- [ ] In Express mode, is top-level code structured without `app = App(app_ui, server)`?
- [ ] In Core modules, are module UI and server instance IDs matching between UI calls (`mod_ui("id_1")`) and server calls (`mod_server("id_1")`)?
- [ ] Are module instance IDs unique within their calling scope?

## 2. Reactivity & Purity Checklist
- [ ] Are reactive values/calcs called with parentheses (`val()`) when reading their value?
- [ ] Are `@reactive.calc` functions purely functional, without mutating external state (`.set()`, database writes, network calls)?
- [ ] Are action buttons and explicit triggers paired with `@reactive.event(...)`?
- [ ] Do action effects stay idle during session initialization? Check initial button values and `ignore_none` / `ignore_init` when relevant.
- [ ] Is `with reactive.isolate():` used wherever reactive values must be read without registering an invalidation dependency?
- [ ] Are mutable collections (lists, dicts) assigned a new reference or copied before updating a `reactive.value`?

## 3. Concurrency & Async Health Checklist
- [ ] Are all synchronous blocking calls (`time.sleep()`, synchronous `requests`, heavy blocking SQL queries) eliminated from server callbacks?
- [ ] If `@reactive.extended_task` is used for blocking synchronous I/O, is it offloaded with `await asyncio.to_thread(...)` or a thread pool?
- [ ] If `@reactive.extended_task` is used for heavy CPU computation, is it offloaded to a `ProcessPoolExecutor`?
- [ ] Are `@reactive.extended_task` functions free of direct reactive reads (`input.x()`, `reactive.value()`), receiving all needed inputs/reactive values as parameters passed during invocation from reactive context? Extended tasks cannot directly read reactive sources.
- [ ] Are intermediate expensive computations cached using `@reactive.calc`?

## 4. UI / Server Contract Checklist
- [ ] In Core mode, does each renderer's effective output ID match an existing `ui.output_xxx("name")` ID (by default the function name, or overridden via `@output(id="...")`)?
- [ ] Are all UI element IDs unique within their namespace?
- [ ] Are R Shiny idioms (`shinyApp`, `fluidPage`, `reactiveVal`, `observeEvent`, `renderUI`) eliminated and replaced with Python Shiny equivalents?

## 5. Session Scope & Security Checklist
- [ ] In Core, is user-specific state initialized inside `server()`? In Express, is it in `app.py`'s per-session scope rather than an imported module?
- [ ] Is shared `reactive.file_reader()` data appropriate for all users and treated as read-only?
- [ ] Are database sessions, user auth context, and state isolated per connection?
- [ ] Are sensitive environment variables, secrets, database credentials, and auth tokens kept on the server and never accidentally rendered or exposed in client UI outputs?

## 6. Startup & Performance Checklist
- [ ] Have process startup and time to first output for a new session been measured separately?
- [ ] Is expensive application-wide initialization outside Core `server()` or in an imported module for Express, rather than repeated in `app.py`?
- [ ] Is slow work needed only after an action deferred, using `@reactive.extended_task` when reactive processing must remain responsive?

## 7. Runtime Verification Checklist
- [ ] Has syntax and module import been verified with `python -c "import app"`?
- [ ] Has a connected browser test exercised session initialization, WebSocket updates, and rendered outputs? A passing connected test also verifies startup.
- [ ] For session leaks or blocking work, have two connected sessions been exercised while the slow operation runs, with click-time input and service latency checked?
- [ ] Have automated test suites (e.g. `pytest` or `unittest`) been run to verify reactive behavior and isolate regressions?
- [ ] Are all background processes (if any were started) cleanly shut down?
