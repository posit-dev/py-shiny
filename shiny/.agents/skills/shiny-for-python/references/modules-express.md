
# Shiny for Python modules (Express mode)

## Overview

In Express mode a module is a **single function** — UI and server code together —
decorated with `@module` from `shiny.express`. This differs from Core mode, which
splits a module into a `@module.ui` / `@module.server` pair. As in Core, the
framework **namespaces every input/output id automatically** per instance, so
reach for a module instead of copy-pasting an Express block or hand-prefixing ids
like `"counter1_button"`.

Call the decorated function once per instance, passing a unique `id` first.

## End-to-end example

```python
from shiny import reactive
from shiny.express import module, render, ui


# One function holds BOTH the UI and the reactive logic.
# First three params are always input, output, session; then your own args.
@module
def counter(input, output, session, label, starting_value: int = 0):
    count = reactive.value(starting_value)

    with ui.card():                     # UI is written inline, in place
        ui.h2(f"This is {label}")
        ui.input_action_button("button", label)   # bare id, auto-namespaced

        @render.text
        def out():
            return f"Click count is {count()}"

    @reactive.effect
    @reactive.event(input.button)       # refer to ids WITHOUT the namespace
    def _():
        count.set(count() + 1)


# Use the module twice; ids must be unique per instance.
counter("counter1", "Counter 1")
ui.hr()
counter("counter2", "Counter 2", starting_value=100)
```

## Pass data in

Add parameters after `input, output, session`. Pass a **reactive** in by handing
the caller's reactive itself (`counter("id", data=my_calc)`) and calling it
(`data()`) inside the module. Returning values out is uncommon in Express because
each instance renders where it is called; when you do return a reactive, capture
it from the call (`total = counter("id")`).

## Nesting modules

A module function can call another module function; because you use bare ids
inside each, the framework composes namespaces (`outer-inner-button`) for you —
never assemble that string yourself.

## Quick reference

| Need | API |
|---|---|
| Import | `from shiny.express import module` |
| Define a module | `@module` on one function `(input, output, session, ...)` |
| Place an instance | `foo("id", ...extra args)` (call it where the UI should appear) |
| Link UI to logic | automatic — they live in the same function |
| Pass reactive data in | extra param; call it inside the module |
| Namespaced id (rare) | `session.make_scope(id).ns("child_id")` |
| Core equivalent | see `references/modules-core.md` |

## Common mistakes

- **Reaching for `@module.ui` / `@module.server`** in an Express app → that is
  the Core API. In Express use the single `@module` decorator; one function,
  called once per instance.
- **Manually prefixing ids** (`"counter1_button"`) → the framework namespaces
  already; use the bare id (`"button"`) in both `ui.*` and `input.*`.
- **Adding an explicit `id` parameter** to the function → the first three params
  must be `input, output, session`; the `id` is supplied at the call site, not
  in the signature.
- **Reusing the same id** for two instances → collisions return; each instance
  needs a distinct id.
- **Not calling the module** (only defining it) → an Express module renders
  nothing until you call `foo("id")` at the point where its UI belongs.
