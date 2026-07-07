# Architecture

Deep-dive into py-shiny's internals. Key implementation files are listed with
each section; the "Key Files" section of `CLAUDE.md` has the consolidated list.

## Reactive System

Implementation: `shiny/reactive/_core.py` (graph machinery),
`shiny/reactive/_reactives.py` (primitives).

The reactive system is based on a **push-pull** model with three core abstractions:

- **Context**: Tracks reactive dependencies during execution. When a reactive
  consumer (Calc/Effect) runs, it creates a Context that records which reactive
  sources (Value) it reads from.
- **Dependents**: Each reactive source maintains a list of downstream consumers
  that depend on it. When a source invalidates, it notifies all dependents.
- **ReactiveEnvironment**: Global singleton managing the reactive graph,
  execution queue, and flush cycles.

Key implementation details:

- `Value()` is the reactive source (observable)
- `Calc_()` is a cached computed value (recomputes only when dependencies change)
- `Effect_()` is a side-effect that re-executes when dependencies change
- `event()` decorator suppresses reactive dependencies for specific reads
- The reactive graph is built automatically through the Context's dependency tracking
- Execution uses a priority queue to ensure correct invalidation ordering
- In tests, `reactive.flush()` forces a synchronous flush of the reactive graph

## Session Hierarchy

Implementation: `shiny/session/_session.py`; app entry point in `shiny/_app.py`.

Sessions manage the lifetime and state of a Shiny application:

- **Session (ABC)**: Base interface defining core session operations
- **AppSession**: Concrete implementation for a single user's session
- **SessionProxy**: Thread-safe proxy that delegates to the appropriate AppSession
- **Inputs/Outputs**: Dynamic objects providing dict-like access to input/output values

Session management:

- Each WebSocket connection gets its own AppSession
- `get_current_session()` retrieves the current session from thread-local or
  async context
- Sessions track input values, output invalidations, file uploads, downloads,
  and more
- Session context is established using the `session_context(session)` context
  manager

## Express vs Core Mode

Implementation: `shiny/express/_run.py` (execution),
`shiny/express/_node_transformers.py` (AST transformation).

**Core mode** is imperative: you explicitly construct UI and define server
logic in a function.

**Express mode** transforms Python code using AST manipulation:

- `@render.text` decorators are hoisted into a synthetic `server()` function
- UI elements are collected into a synthetic `ui` object
- Top-level code runs in a special context where UI calls are recorded
- `RecallContextManager` enables UI elements to render themselves automatically
- The transformation happens at import time via `_run.py` and
  `_node_transformers.py`

Critical difference: Express mode uses **execution order** (top-to-bottom) for
UI layout, while Core mode uses explicit nesting. Debugging Express apps
requires understanding the transformed code.

## HTML Generation and Dependencies

HTML is generated using the `htmltools` package:

- UI functions return `Tag` or `TagList` objects
- Tags are mutable; use `.add_class()`, `.add_style()`, `.attrs()` to modify
- HTML dependencies are attached to tags and automatically bundled
- `components_dependencies()` returns bslib component dependencies

Asset vendoring (bslib CSS/JS, theme presets, `make upgrade-html-deps`) is
covered in `.claude/references/assets.md`.

## Input/Output Bindings

Client-server communication works through bindings:

**Input bindings** (client → server):

- Registered via CSS class selectors in TypeScript (e.g., `.bslib-input-foo`)
- Implement `getValue()`, `setValue()`, `subscribe()` methods
- Send values to server using `Shiny.setInputValue(id, value)`
- Server receives via `input.foo()` which returns a reactive Value

**Output bindings** (server → client):

- Server defines output using `@render.text`, `@render.plot`, etc.
- Renderers inherit from the `Renderer` base class
  (`shiny/render/renderer/_renderer.py`; see
  `.claude/references/component-patterns.md` for the implementation pattern)
- Client subscribes to output via `Shiny.bindOutput()` in TypeScript
- Updates are sent as messages through the WebSocket

**Update functions**:

- Use `session.send_input_message()` to update input widgets from the server
- Client handles via `receiveMessage()` in the input binding

## Module System

Implementation: `shiny/_namespaces.py` manages the namespace stack;
`shiny/module.py` provides the decorators.

Modules enable namespaced, reusable components:

- `@module.ui` decorator creates a UI function with automatic ID namespacing
- `@module.server` decorator creates a server function with namespace context
- Inside a module, use `resolve_id()` to namespace IDs
- `resolve_id_or_none()` for optional namespacing
- Modules can be nested; namespaces compose with `parent-child` format

## Testing Architecture

**Unit tests** (`tests/pytest/`):

- Use standard pytest with syrupy for snapshots (`make test-update-snapshots`
  to regenerate)
- Focus on Python API correctness, parameter validation, edge cases
- Run with `make test` or `pytest`

**Playwright tests** (`tests/playwright/`):

- End-to-end tests using Playwright with custom controllers
- Controllers in `shiny/playwright/controller/` provide high-level APIs for
  interacting with inputs/outputs
- Each input component should have a controller class
- Test apps live alongside test files
- Suites: `tests/playwright/shiny/` (`make playwright-shiny`),
  `tests/playwright/examples/` (`make playwright-examples`),
  `tests/playwright/deploys/`, `tests/playwright/ai_generated_apps/`
- Run with `make playwright` (all browsers) or `make playwright-debug`
  (chromium, headed)
- Prefer `.expect_*()` controller methods, which auto-wait, over manual sleeps

**Playwright controller pattern**:

```python
from shiny.playwright.controller import InputText, OutputText

text_input = InputText(page, "my_input")
text_input.set("foo")
text_input.expect_value("foo")

text_output = OutputText(page, "my_output")
text_output.expect_value("You entered: foo")
```

## JavaScript/TypeScript Build

Client-side code is in `js/` (entry point `js/src/shiny/index.ts`), bundled
with esbuild into `shiny/www/shared/py-shiny/`. Build commands and workflow are
covered in `.claude/references/assets.md`.
