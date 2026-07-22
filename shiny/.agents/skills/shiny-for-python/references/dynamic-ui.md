
# Dynamic UI in Shiny for Python (Core)

## Overview

UI does not have to be fixed at startup. Prefer, in order: render a reactive
chunk with `@render.ui`; adjust an existing input in place with a `ui.update_*`
function; and only for arbitrary, persistent injection reach for
`ui.insert_ui` / `ui.remove_ui`. To merely show or hide static UI based on
input values, use `ui.panel_conditional` — it runs client-side with no server
round-trip.

Do NOT rebuild the whole page, write custom JavaScript to poke the DOM, or
hard-code every possible input state and toggle visibility by hand. Reactivity
(`@reactive.effect`; see `references/reactivity.md`) drives all of this.

This documents the Core form. In Express mode, use `@render.express` instead of
`@render.ui` (see `references/express.md`); everything else below is identical.

## Compute UI reactively: `@render.ui` + `ui.output_ui`

The primary approach. Put an `output_ui(id)` placeholder in the UI, then a
`@render.ui` function whose name matches the id returns any UI object. It
re-runs whenever a reactive source it reads changes.

```python
from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_select("kind", "Control", ["slider", "text"]),
    ui.output_ui("control"),
)

def server(input: Inputs, output: Outputs, session: Session):
    @render.ui
    def control():
        if input.kind() == "slider":
            return ui.input_slider("n", "N", min=1, max=100, value=50)
        return ui.input_text("label", "Label")

app = App(app_ui, server)
```

## Update an existing input: `ui.update_*`

Change a control's value, label, or choices without recreating it. Match the
function to the input type (`update_select`, `update_text`, `update_numeric`,
`update_slider`, `update_checkbox`, `update_date`, `update_action_button`, ...).
**Call it inside a `@reactive.effect`** — calling `update_*` at server top level
runs once with no dependencies and never reacts.

```python
from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_select("country", "Country", ["US", "CA"]),
    ui.input_select("city", "City", []),
)

def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    def _():
        cities = {"US": ["NYC", "LA"], "CA": ["Toronto", "Montreal"]}
        ui.update_select("city", choices=cities[input.country()])

app = App(app_ui, server)
```

## Inject / remove arbitrary UI: `ui.insert_ui` / `ui.remove_ui`

Use sparingly, when you need UI that persists and accumulates (e.g. a button
that adds a new row each click). Inserted UI stays until removed — unlike
`@render.ui`, it is not managed for you. `selector` is a jQuery/CSS selector.

```python
from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(ui.input_action_button("add", "Add field"))

def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.add)
    def _():
        ui.insert_ui(
            ui.input_text(f"txt_{input.add()}", "Enter text"),
            selector="#add",
            where="afterEnd",
        )

app = App(app_ui, server)
```

Remove with `ui.remove_ui(selector=...)`. Inputs are wrapped in a `<div>`, so
target the wrapper: `ui.remove_ui("div:has(> #txt_1)")`.

## Show / hide UI client-side: `ui.panel_conditional`

Wrap UI in `panel_conditional(condition, ...)` where `condition` is a
JavaScript expression over input values (e.g. `"input.show"`). Toggling is
instant and needs no server. The UI still exists and its inputs stay
registered when hidden.

```python
from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_fluid(
    ui.input_checkbox("advanced", "Show advanced", False),
    ui.panel_conditional(
        "input.advanced",
        ui.input_slider("threshold", "Threshold", min=0, max=1, value=0.5),
    ),
)

def server(input: Inputs, output: Outputs, session: Session):
    pass

app = App(app_ui, server)
```

## Quick reference

| Need | Use |
|---|---|
| UI that depends on inputs/data | `@render.ui` + `ui.output_ui(id)` |
| Express: same, capture syntax | `@render.express` (see `references/express.md`) |
| Change an input's value/label/choices | `ui.update_*(id, ...)` in a `@reactive.effect` |
| Inject persistent/accumulating UI | `ui.insert_ui(ui, selector, where=)` |
| Remove injected UI | `ui.remove_ui(selector)` |
| Show/hide static UI, no round-trip | `ui.panel_conditional("input.x", ...)` |
| Insert/update nav or tab panels | see `references/navigation.md` (`nav_insert`, `update_navs`) |

## Common mistakes

- `ui.update_*` called at server top level (not in an effect) -> runs once and
  never reacts. Wrap it in `@reactive.effect`.
- `@render.ui` function name does not match its `ui.output_ui(id)` -> nothing
  renders. The function name (or `@output(id=...)`) must equal the id.
- Reaching for `insert_ui` to swap between input variants -> use `@render.ui`;
  `insert_ui` UI accumulates and must be removed manually.
- `remove_ui("#txt")` targets the input, not its wrapper `<div>`, and leaves the
  label -> use a wrapper selector like `"div:has(> #txt)"`.
- Using `panel_conditional` when the shown/hidden content depends on server-side
  data -> that's a `@render.ui` job; `panel_conditional` only tests client-side
  input values in JavaScript (`input.x`, `&&`, `===`), not Python.
