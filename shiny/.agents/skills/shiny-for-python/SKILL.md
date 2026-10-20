---
name: shiny-for-python
description: "Use this skill when building, modifying, debugging, testing, or reviewing a Shiny for Python (py-shiny) app - anything importing `shiny` or `shiny.express` or run with `shiny run`. It covers UI, layout, and theming; reactivity; outputs and renderers; modules; sessions and background tasks; troubleshooting misbehaving apps; and testing. This official skill ships with the installed `shiny` package, so its guidance should match your version; it's a short index linking to per-topic reference guides, so opening it adds little context and routes you to the one guide relevant to the task. Reach for it before hand-rolling what the framework already provides, such as custom HTML tables, DOM manipulation, or polling loops."
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
| Reactivity | A value should recompute or an output update as inputs change; choosing between calc / effect / value; `req`, `isolate`, timers, polling, setting values from background tasks | `references/reactivity.md` |
| Express mode | Writing or converting an Express app (`from shiny.express import ...`); context-manager layout; `page_opts`, `@expressify` | `references/express.md` |
| Modules (Core) | A reusable, repeatable UI+server component in a Core app; avoiding input/output id collisions across copies | `references/modules-core.md` |
| Modules (Express) | The same reusable-component need in an Express app, via the single `@module` decorator | `references/modules-express.md` |
| Session lifecycle | Per-session cleanup (`on_ended`), reading request headers/cookies/URL, flush hooks, per-session routes | `references/session-lifecycle.md` |

## Dashboard building

| Topic | Use when | Reference |
|---|---|---|
| Dashboard design | Turning a dataset or brief into a polished analytical dashboard; planning information hierarchy, shared filters, responsive layout, empty states, and the final visual/functional quality pass | `references/dashboard-design.md` |
| Dashboard components | Composing cards, KPI value boxes, local card toolbars, accessible icons, tooltips, and popovers | `references/dashboard-components.md` |
| Interactive charts | Rendering Plotly charts with shinywidgets; choosing chart forms, applying a coherent visual system, formatting hover/data labels, and handling empty data | `references/interactive-charts.md` |
| Maps | Choosing and rendering a geographic widget; cleaning coordinates, avoiding overplotting, and selecting Plotly, ipyleaflet, or lonboard by interaction and scale | `references/maps.md` |

## Layout & navigation

| Topic | Use when | Reference |
|---|---|---|
| Layouts | Arranging a page into cards, columns, sidebars, value boxes, or accordions (bslib containers) | `references/layouts.md` |
| Navigation | Tabs, pills, or a navbar with multiple pages; reading/switching the active tab; runtime nav panels | `references/navigation.md` |
| Dynamic UI | Wiring Core output IDs, keeping UI IDs unique, or UI that changes after render — `@render.ui`, `ui.update_*`, `insert_ui`/`remove_ui`, `panel_conditional` | `references/dynamic-ui.md` |
| Theming | Colors, fonts, Bootswatch presets, Sass variables, brand.yml, light/dark mode via `ui.Theme` | `references/theming.md` |

## Outputs & rendering

| Topic | Use when | Reference |
|---|---|---|
| Static plots & images | Rendering matplotlib/seaborn/plotnine figures or images; static plot click/hover/brush interactions. For Plotly, read Interactive charts above | `references/plots.md` |
| Data frames | Interactive tables via `@render.data_frame` (DataGrid/DataTable) — sort, filter, select, edit | `references/data-frames.md` |
| Files | File uploads (`ui.input_file`) and generated-file downloads (`@render.download_button`/`@render.download_link`) | `references/files.md` |

## Feedback & interactivity

| Topic | Use when | Reference |
|---|---|---|
| Feedback | Toasts/notifications, modal dialogs, progress bars, busy indicators | `references/feedback.md` |
| Extended tasks | Running slow work outside the session's reactive cycle so the session stays responsive; task buttons | `references/extended-tasks.md` |
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
| Troubleshooting | An existing app misbehaves: blank outputs, stale values, cross-session leakage, frozen sessions, or ID mismatches; auditing an app for these issues | `references/troubleshooting.md` |
| Test server | Testing server logic in memory with the `local_server` fixture / `test_server()` — set inputs, assert on outputs/exports, module scopes; no browser | `references/test-server.md` |
| Testing | End-to-end Playwright tests — launching an app under pytest, locating and asserting on UI | `references/testing.md` |
| Debugging | Inspecting server-side reactive/input/output state; exposing values to a test harness | `references/debugging.md` |
| OpenTelemetry | OTel tracing/profiling of reactive execution; exporting spans to a backend | `references/otel.md` |
