
# Writing Shiny Express apps

## Overview

In **Express mode**, the app file *is* the app. Top-level statements build the
UI as the file executes, and `@render.*` functions defined at the top level
place their output where they are written. There is no explicit `app_ui`
object and no `server()` function, and you never construct an `App(...)` — Shiny
detects an Express app by the presence of `from shiny.express import ...` and
wires it up for you.

Do **not** try to add a Core-style `app_ui = ...` / `def server(...)` split, and
do **not** nest UI calls as positional arguments the Core way. Express uses
`with` blocks for layout containers instead.

## The Express import and mental model

```python
from shiny.express import input, render, ui

ui.input_slider("n", "N", 1, 100, 50)  # rendered where it appears

@render.text
def out():
    return f"n = {input.n()}"        # rendered where it appears
```

- `input` — read reactive input values: `input.n()`.
- `render` — output decorators (`render.text`, `render.plot`, `render.table`,
  `render.data_frame`, `render.ui`, ...). A decorated function renders in place;
  you do **not** also add an `output_*()` placeholder (Core does).
- `ui` — Express UI: inputs, plus **context-manager** layout containers.
- `session` is also importable (`from shiny.express import session`) for
  lifecycle hooks, bookmarking, etc.

## Layout with context managers

Core nests components as arguments; Express opens a `with` block and puts
children inside it.

```python
from shiny.express import input, render, ui

with ui.sidebar():
    ui.input_select("var", "Variable", choices=["a", "b"])

with ui.layout_columns():
    with ui.card():
        ui.card_header("Left")

        @render.plot
        def hist(): ...

    with ui.card():
        ui.card_header("Right")
```

Common container managers: `ui.sidebar()`, `ui.card()`, `ui.layout_columns()`,
`ui.layout_column_wrap()`, `ui.layout_sidebar()`, `ui.accordion()` /
`ui.accordion_panel()`, `ui.nav_panel()` and the `ui.navset_*()` family,
`ui.value_box()`, `ui.popover()`, `ui.tooltip()`, `ui.panel_well()`.

## Page-level options

Instead of choosing a `page_*()` function, call `ui.page_opts()` once at the top:

```python
from shiny.express import ui

ui.page_opts(title="My app", fillable=True)
```

The page function is chosen automatically: a top-level `ui.nav_panel()` yields a
navbar page, a top-level `with ui.sidebar():` yields a sidebar page, otherwise
`fillable`/`full_width` pick between fixed, fluid, and fillable layouts.

## Same app: Core vs Express

```python
# --- Core ---
from shiny import App, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(ui.input_select("var", "Variable", choices=["a", "b"])),
    ui.output_plot("hist"),
    title="Hello sidebar!",
)

def server(input, output, session):
    @render.plot
    def hist(): ...

app = App(app_ui, server)
```

```python
# --- Express (same app) ---
from shiny.express import input, render, ui

ui.page_opts(title="Hello sidebar!")

with ui.sidebar():
    ui.input_select("var", "Variable", choices=["a", "b"])

@render.plot
def hist(): ...
```

## Reusable UI with `@expressify`

A plain function called at the top level only contributes its return value. To
make a helper emit UI line-by-line like the top level, decorate it with
`@expressify`:

```python
from shiny.express import expressify, ui

@expressify
def labeled_card(title: str):
    with ui.card():
        ui.card_header(title)
        ui.markdown("Body content")

labeled_card("First")
labeled_card("Second")
```

Use `ui.hold()` (a context manager) to capture UI without displaying it, so you
can place it elsewhere (e.g. pass it as a `footer=`).

## Express modules

For reusable, namespaced components, Express uses a single `@module` decorator
(`from shiny.express import module`) — the counterpart to Core's
`module.ui()` / `module.server()` pair. See `references/modules-express.md` for
the full pattern.

## When to choose Express vs Core

- **Express**: rapid, linear, single-file apps; dashboards; prototypes;
  notebooks-to-app. Less boilerplate.
- **Core**: large or highly structured apps, dynamic UI assembled
  programmatically, or when you want the UI as a first-class value to inspect,
  reuse, or return from functions.
- An app file is **either** Express or Core, never both. You cannot mix
  `from shiny.express import ...` with `App(app_ui, server)` in one file.

## Quick reference (Core → Express)

| Core | Express |
|---|---|
| `from shiny import App, render, ui` | `from shiny.express import input, render, ui` |
| `app_ui = ui.page_sidebar(...)` + `App(app_ui, server)` | top-level code; no `App(...)` |
| `def server(input, output, session):` | no server function; define outputs at top level |
| `ui.page_*(..., title=...)` | `ui.page_opts(title=...)` |
| `ui.sidebar(child1, child2)` | `with ui.sidebar():` then children |
| `ui.card(ui.output_plot("p"))` + `@render.plot def p()` | `with ui.card():` then `@render.plot def p()` |
| `module.ui()` + `module.server()` | `@module` on one Express function (see `references/modules-express.md`) |
| reusable UI helper returning a Tag | `@expressify` helper emitting UI |

## Common mistakes

- Adding `app_ui = ...`, `def server(...)`, or `app = App(...)` in an Express
  file → Express has no such split; delete them and write top-level code.
- Adding `ui.output_plot("hist")` *and* a `@render.plot def hist()` → the
  decorated function renders in place; the extra placeholder is Core-only.
- Nesting layout the Core way (`ui.card(ui.card_header(...), ...)`) inside
  Express → use `with ui.card():` and put children in the block.
- A helper function that builds UI shows nothing → decorate it with
  `@expressify` (or return a single Tag/TagList and display that).
- Calling `ui.page_opts()` or importing `shiny.ui`'s `page_*()` functions in
  Express → page layout is automatic; use `ui.page_opts()` only.
- Mixing Core and Express imports in one file → pick one mode per file.
