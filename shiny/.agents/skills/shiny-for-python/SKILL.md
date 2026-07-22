---
name: shiny-for-python
description: Building, styling, testing, debugging, or observing a Shiny for Python (py-shiny) reactive web app - `from shiny import ...`, `shiny run app.py`. Index skill: read this, then open the linked reference for the area you are working in. Covers reactivity (calc/effect/value/event/req/isolate); Express vs Core mode; modules; layout, navigation, dynamic UI, and theming; outputs (plots, data frames, file upload/download, custom renderers); LLM chat and Markdown streaming; notifications, modals, and progress; extended (background) tasks; bookmarking; custom JS input/output components; session lifecycle; Playwright end-to-end testing; server-side debugging; and OpenTelemetry. Use when writing or changing any Shiny for Python app, or when tempted to hand-roll what the framework provides - a custom HTML table, fake tabs, manual DOM manipulation, blocking work inside reactive code, polling loops, or print-debugging server state.
---

# Shiny for Python

Shiny for Python (py-shiny) builds reactive web apps in pure Python. Two modes:
**Core** (an explicit `app_ui` object plus a `server(input, output, session)`
function) and **Express** (top-level code in the app file *is* the UI, with
outputs defined inline). The reactive graph is the engine: reading a reactive
source (`input.x()`, a `reactive.value`, a `@reactive.calc`) inside a reactive
context registers a dependency, so changing that source re-runs everything that
read it — you never call outputs or schedule updates yourself.

This skill is an **index**. Find your task below and **read the linked
reference file before writing code** for that area.

## Foundations

| Topic | Use when | Reference |
|---|---|---|
| Reactivity | A value should recompute or an output update as inputs change; choosing between calc / effect / value; `req`, `isolate`, timers, polling | `references/reactivity.md` |
| Express mode | Writing or converting an Express app (`from shiny.express import ...`); context-manager layout; `page_opts`, `@expressify` | `references/express.md` |
| Modules (Core) | A reusable, repeatable UI+server component in a Core app; avoiding input/output id collisions across copies | `references/modules-core.md` |
| Modules (Express) | The same reusable-component need in an Express app, via the single `@module` decorator | `references/modules-express.md` |
| Session lifecycle | Per-session cleanup (`on_ended`), reading request headers/cookies/URL, flush hooks, per-session routes | `references/session-lifecycle.md` |

## Layout & navigation

| Topic | Use when | Reference |
|---|---|---|
| Layouts | Arranging a page into cards, columns, sidebars, value boxes, or accordions (bslib containers) | `references/layouts.md` |
| Navigation | Tabs, pills, or a navbar with multiple pages; reading/switching the active tab; runtime nav panels | `references/navigation.md` |
| Dynamic UI | UI that changes after render — `@render.ui`, `ui.update_*`, `insert_ui`/`remove_ui`, `panel_conditional` | `references/dynamic-ui.md` |
| Theming | Colors, fonts, Bootswatch presets, Sass variables, brand.yml, light/dark mode via `ui.Theme` | `references/theming.md` |

## Outputs & rendering

| Topic | Use when | Reference |
|---|---|---|
| Plots & images | Rendering matplotlib/seaborn/plotnine figures or images; plot click/hover/brush interactions | `references/plots.md` |
| Data frames | Interactive tables via `@render.data_frame` (DataGrid/DataTable) — sort, filter, select, edit | `references/data-frames.md` |
| Files | File uploads (`ui.input_file`) and generated-file downloads (`@render.download`) | `references/files.md` |

## Feedback & interactivity

| Topic | Use when | Reference |
|---|---|---|
| Feedback | Toasts/notifications, modal dialogs, progress bars, busy indicators | `references/feedback.md` |
| Extended tasks | Running slow work off the reactive flush without freezing the app; task buttons | `references/extended-tasks.md` |
| Bookmarking | Saving/restoring app state — shareable URLs, refresh persistence, server-side state | `references/bookmarking.md` |

## AI & streaming

| Topic | Use when | Reference |
|---|---|---|
| Chat | Building an LLM chatbot with `ui.Chat` — streaming responses, wiring a provider, chat history | `references/chat.md` |
| Markdown streaming | Streaming Markdown/LLM text into a non-chat region with `ui.MarkdownStream` | `references/markdown-streaming.md` |

## Extending Shiny

| Topic | Use when | Reference |
|---|---|---|
| Custom renderers | Authoring a reusable `@render.xxx` decorator by subclassing `shiny.render.renderer.Renderer` | `references/custom-renderers.md` |
| Custom components | Integrating custom browser JS — custom input/output bindings, `send_custom_message`, HTMLDependency assets | `references/custom-components.md` |

## Testing & observability

| Topic | Use when | Reference |
|---|---|---|
| Testing | End-to-end Playwright tests — launching an app under pytest, locating and asserting on UI | `references/testing.md` |
| Debugging | Inspecting server-side reactive/input/output state; exposing values to a test harness | `references/debugging.md` |
| OpenTelemetry | OTel tracing/profiling of reactive execution; exporting spans to a backend | `references/otel.md` |
