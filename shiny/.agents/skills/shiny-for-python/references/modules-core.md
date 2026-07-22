---
name: modules-core
description: Use when a Shiny for Python (py-shiny) Core-mode app (explicit app_ui + server) needs a reusable, repeatable UI+server component - the same widget or panel appearing multiple times, avoiding input/output id collisions across copies, sharing one piece of server logic, destroying a dynamically added module instance, or when tempted to manually prefix input ids (like "counter1_button") or copy-paste server functions to make ids unique. For Express-mode apps, use the modules-express skill instead.
---

# Shiny for Python modules (Core mode)

## Overview

A module is a reusable pair of functions — a UI function and a server function —
that can be dropped into an app (or another module) more than once without id
collisions. The framework **namespaces every input/output id automatically** for
each instance. Reach for a module instead of copy-pasting server logic or
hand-prefixing ids like `"counter1_button"`, `"counter2_button"`.

A module has two halves linked by a shared instance `id`:

- `@module.ui` — builds the HTML. The decorator injects a leading `id` argument.
- `@module.server` — the reactive logic. You write the function with
  `input, output, session` as its first parameters, but you **call** it with a
  leading `id` instead (`foo_server("counter1")`); the decorator supplies
  `input, output, session` for that namespace automatically.

Calling `foo_ui("counter1")` and `foo_server("counter1")` with the **same id**
wires that UI instance to that server instance.

## End-to-end example

```python
from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui


# --- Module UI: do NOT add an `id` param; the decorator injects it. ---
@module.ui
def counter_ui(label: str = "Increment") -> ui.TagChild:
    return ui.card(
        ui.h2(label),
        ui.input_action_button("button", label),  # plain id, auto-namespaced
        ui.output_text("out"),
    )


# --- Module server: starts with input/output/session, then extra args. ---
@module.server
def counter_server(
    input: Inputs, output: Outputs, session: Session, start: int = 0
):
    count = reactive.value(start)

    @reactive.effect
    @reactive.event(input.button)       # refer to ids WITHOUT the namespace
    def _():
        count.set(count() + 1)

    @render.text
    def out() -> str:
        return f"Count is {count()}"

    return count                        # expose a value to the caller


# --- App uses the module twice; ids must be unique per instance. ---
app_ui = ui.page_fluid(
    counter_ui("counter1", "Counter 1"),
    counter_ui("counter2", "Counter 2"),
)


def server(input: Inputs, output: Outputs, session: Session):
    counter_server("counter1")
    total = counter_server("counter2", start=100)

    @render.text
    def _():
        return f"Second counter: {total()}"


app = App(app_ui, server)
```

## Pass data in, get values out

- **In:** add parameters after `input, output, session` on the server function
  (and after the label params on the UI function). Pass **reactive** inputs by
  handing the caller's reactive itself, e.g. `foo_server("id", data=my_calc)`,
  and call `data()` inside the module.
- **Out:** `return` reactives (calcs/values) or plain values from the server
  function. The caller receives whatever you return, as shown above with
  `total`.

## Reading a nested module's input from outside

Inside a module, refer to ids by their bare name (`input.button`). From the
**parent**, the same input lives under the namespace. Prefer returning a value
from the server function over reaching in. When you must resolve a namespaced
id (e.g. for `input[...]` or a manual selector), build it with the module's
`session` scope rather than string-concatenating:

```python
child = session.make_scope("counter1")
resolved = child.ns("button")   # -> "counter1-button"
```

## Nesting modules

A module UI can call another module's UI, and a module server can call another
module's server. Because you use bare ids inside each module, the framework
composes the namespaces (`outer-inner-button`) for you — never assemble that
string yourself.

## Remove a dynamically added module

When you add module instances at runtime (e.g. with `ui.insert_ui`) and later
remove them, tear down the instance's reactive graph too, or its effects keep
firing (duplicate observers, repeated side effects). `session.destroy(id)` is
**async** and destroys everything under that namespace:

```python
@reactive.effect
async def _():
    ...
    ui.remove_ui(f"#{mod_id}")
    await session.destroy(mod_id)   # tear down that instance's reactive graph
```

`destroy` wipes the instance's state. If a value must **persist** across
add/remove cycles, keep a `reactive.value` created *outside* the module and pass
it in; update it from within the module. Then destroying the instance leaves the
value intact for the next instance.

## Express mode

Express-mode apps use a different, single-decorator module API. See the
**modules-express** skill.

## Quick reference

| Need | API |
|---|---|
| Define module UI | `@module.ui` (first arg `id` is injected) |
| Define module server | `@module.server` with `(input, output, session, ...)` |
| Place an instance | `foo_ui("id", ...ui args)` |
| Activate its logic | `foo_server("id", ...extra args)` |
| Link UI to server | pass the **same** `id` string to both |
| Pass reactive data in | extra server param; call it inside the module |
| Send values out | `return` from the server function |
| Namespaced id (rare) | `session.make_scope(id).ns("child_id")` |
| Destroy a dynamic instance | `await session.destroy(id)` (async) |
| Express equivalent | see the **modules-express** skill |

## Common mistakes

- **Manually prefixing ids** inside a module (`"counter1_button"`) → the
  framework already namespaces; use the bare id (`"button"`) in both `ui.*`
  and `input.*`. Manual prefixes break the wiring.
- **Adding an `id` parameter** to the `@module.ui` function → the decorator
  injects it; a second one shifts your other args.
- **Mismatched ids** between `foo_ui("a")` and `foo_server("b")` → the UI and
  server never connect and outputs stay blank. Use one shared id.
- **Reusing the same id** for two instances → collisions return. Each instance
  needs a distinct id.
- **Reaching into a module's inputs from the parent** via a guessed string like
  `input["counter1_button"]` → return the value from the server function
  instead, or resolve the id with `session.make_scope(id).ns(...)`.
- **Keeping `input, output, session`** in the *call* (`foo_server(input, ...)`)
  → the decorator removed them; call with the `id` first: `foo_server("id")`.
