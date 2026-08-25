# Shiny Doctor Diagnostic Checklist & Workflow

This reference provides a step-by-step audit workflow for validating and diagnosing a Shiny for Python codebase.

---

## 1. Syntax & Imports Audit
- [ ] Are imports using `shiny` or `shiny.express` consistently without cross-mode collision?
- [ ] Are R Shiny idioms (`shinyApp`, `fluidPage`, `reactiveVal`, `observeEvent`, `renderUI`) eliminated?
- [ ] Are all imported rendering decorators (`@render.text`, `@render.plot`, `@render.data_frame`, `@render.ui`) matching their corresponding outputs?

## 2. Reactivity Audit
- [ ] Are reactive values/calcs called with parentheses (`val()`) when their current value is read?
- [ ] Are `@reactive.calc` functions pure and free of side effects (`.set()`, database writes, network calls)?
- [ ] Are action buttons and explicit triggers wrapped with `@reactive.event(...)`?
- [ ] Is `with reactive.isolate():` used wherever reactive values should be read without triggering dependencies?
- [ ] Are mutable collections (lists, dicts) assigned a new reference or copied before calling `.set()` on a `reactive.value`?

## 3. Concurrency & Performance Audit
- [ ] Are there any synchronous blocking calls (`time.sleep()`, synchronous `requests`, heavy blocking SQL queries) on the main event loop?
- [ ] Are long-running or CPU-intensive tasks moved to `@reactive.extended_task` or async coroutines?
- [ ] Is expensive computation cached using intermediate `@reactive.calc` nodes?
- [ ] Are database connections and sessions properly isolated per client session?

## 4. UI & Server Binding Audit
- [ ] In Core mode, does every `@render.xxx` function name match an existing `ui.output_xxx("name")` ID?
- [ ] In Express mode, are components structured without explicit `app = App(app_ui, server)`?
- [ ] Are all UI element IDs unique within their scope/module?
- [ ] In modular components, are all IDs wrapped with `ns()`?

## 5. Session Scope & Security
- [ ] Are user-specific reactive values initialized inside the `server` function or Express session context (not global module scope)?
- [ ] Are sensitive environment variables, secrets, and auth tokens kept out of client-side UI configurations?
