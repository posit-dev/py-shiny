# Shiny Doctor Diagnostic Checklist & Verification Guide

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
- [ ] Is `with reactive.isolate():` used wherever reactive values must be read without registering an invalidation dependency?
- [ ] Are mutable collections (lists, dicts) assigned a new reference or copied before updating a `reactive.value`?

## 3. Concurrency & Async Health Checklist
- [ ] Are all synchronous blocking calls (`time.sleep()`, synchronous `requests`, heavy blocking SQL queries) eliminated from server callbacks?
- [ ] If `@reactive.extended_task` is used for blocking synchronous I/O, is it offloaded with `await asyncio.to_thread(...)` or a thread pool?
- [ ] If `@reactive.extended_task` is used for heavy CPU computation, is it offloaded to a `ProcessPoolExecutor`?
- [ ] Are intermediate expensive computations cached using `@reactive.calc`?

## 4. UI / Server Contract Checklist
- [ ] In Core mode, does every `@render.xxx` function name match an existing `ui.output_xxx("name")` ID?
- [ ] Are all UI element IDs unique within their namespace?
- [ ] Are R Shiny idioms (`shinyApp`, `fluidPage`, `reactiveVal`, `observeEvent`, `renderUI`) eliminated and replaced with Python Shiny equivalents?

## 5. Session Scope & Security Checklist
- [ ] Are user-specific reactive values initialized inside the `server` function or Express session context (never at global module scope)?
- [ ] Are database sessions, user auth context, and state isolated per connection?

## 6. Runtime Verification Checklist
- [ ] Has the application been launched with `shiny run app.py` to verify import and ASGI server startup without crashes or schema errors?
- [ ] If claiming session-level verification, has a client connection (browser or Playwright test harness using `shiny.pytest` fixtures) been established to exercise the `server()` function, WebSocket connection, and reactive renderers?
- [ ] Have automated tests been rerun to confirm resolution?
- [ ] Has the report been accurately labeled (**Runtime Verified (Session Level)**, **Server Startup Verified**, or **Static Diagnosis Only**)?

