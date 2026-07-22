
# Authoring custom output renderers in Shiny for Python

## Overview

A `Renderer` subclass packages "run this output function, turn its return
value into a JSON-serializable payload, ship it to the browser" into a reusable
`@render.my_thing` decorator. Subclass `shiny.render.renderer.Renderer[IT]`
(`IT` is the type the app author's function returns) and implement two things:
`auto_output_ui()` and either `transform()` (common) or `render()` (rare).

Do NOT copy the same formatting logic into every `@render.ui`/`@render.text`
function, and do NOT reach for `shiny.render.transformer.output_transformer` or
`OutputRenderer` — those are **deprecated/superseded by `Renderer`**. If you
only need custom *client* rendering (a JS widget), you still author the payload
here; the browser side is a separate output binding — see the
`references/custom-components.md`.

## Subclass and transform the value

Implement `async def transform(self, value)` to convert a non-`None` return
value into a JSON-serializable object. The base `render()` calls your value
function, short-circuits on `None` (nothing is sent), and otherwise calls
`transform()`. `auto_output_ui()` returns the default UI placeholder.

```python
from shiny.render.renderer import Renderer, ValueFn
from shiny.ui import output_code


class render_upper(Renderer[str]):
    """Render a string in upper case."""

    def auto_output_ui(self):
        return output_code(self.output_id)

    async def transform(self, value: str) -> str:
        # Only non-None values reach here; return must be JSON-serializable.
        return str(value).upper()
```

Use it like any built-in renderer. `self.output_id` is the decorated function's
name (no module prefix); `self.fn` is the app author's value function, always
wrapped async.

```python
from shiny import App, ui

app_ui = ui.page_fluid(ui.output_code("greeting"))

def server(input, output, session):
    @render_upper
    def greeting():
        return "hello"

app = App(app_ui, server)
```

Implement `render()` **instead of** `transform()` only when you need full
control (e.g. `None` should still send a payload). Never implement both.

```python
async def render(self):
    value = await self.fn()   # None short-circuit is now YOUR responsibility
    return {} if value is None else {"text": str(value)}
```

## Accept decorator arguments

Add an `__init__` that takes the optional value function first, then keyword-only
params. Always call `super().__init__(_fn)` last-ish and store your params. This
enables both `@render_capitalize` and `@render_capitalize(to_case="lower")`.

```python
from typing import Literal, Optional
from shiny.render.renderer import Renderer, ValueFn
from shiny.ui import output_code


class render_capitalize(Renderer[str]):
    def auto_output_ui(self):
        return output_code(self.output_id)

    def __init__(
        self,
        _fn: Optional[ValueFn[str]] = None,
        *,
        to_case: Literal["upper", "lower"] = "upper",
    ) -> None:
        super().__init__(_fn)
        self.to_case = to_case

    async def transform(self, value: str) -> str:
        return value.upper() if self.to_case == "upper" else value.lower()
```

```python
@render_capitalize(to_case="lower")
def title():
    return "SHOUTING"
```

## Core vs Express, and async

`auto_output_ui()` is what makes your renderer work in **Express** with no
`ui.output_*` call — Express auto-renders it. In **Core**, add the matching
`ui.output_*` placeholder whose id equals the function name (as in the first
example). `auto_output_ui()` returns the output placeholder that matches your
renderer, such as `output_code` for `render_capitalize`, or the renderer's
corresponding `ui.output_*` content (see `references/custom-components.md` for wiring
a custom output binding).

The app author's function may be sync **or** async — `self.fn` is always awaited,
so `transform`/`render` are `async` and handle both. Scrub non-deterministic
snapshot values with `self.snapshot_preprocess(fn)` (see `references/testing.md`).

## Quick reference

| Member | Purpose |
|---|---|
| `class MyR(Renderer[IT])` | `IT` = type the app function returns |
| `async def transform(self, value)` | Non-`None` value → JSON-serializable payload (common path) |
| `async def render(self)` | Full control; you call `self.fn()` and handle `None` (rare) |
| `def auto_output_ui(self)` | Default UI placeholder → enables Express; return `ui.output_*` |
| `def __init__(self, _fn=None, *, ...)` | Accept decorator args; call `super().__init__(_fn)` |
| `self.fn` | App author's value function (awaitable, `await self.fn()`) |
| `self.output_id` | Decorated function name / `@output(id=)` (no module prefix) |
| `self.snapshot_preprocess(fn)` | Scrub value for test snapshots only |

## Common mistakes

- Implementing both `transform()` and `render()` → pick one. `render()`
  overrides the base and never calls `transform()`.
- Returning a non-JSON object (a `Figure`, a `datetime`) from
  `transform()` → serialization fails. Return `dict`/`list`/`str`/`int`/`None`.
- Expecting `transform()` to run on `None` → the base `render()` short-circuits
  first; if `None` must send something, override `render()` instead.
- `__init__` not signed `(_fn=None, *, ...)` or not forwarding `_fn` to
  `super().__init__(_fn)` → the bare `@render_x` (no parens) form breaks.
- No `auto_output_ui()` → the renderer errors in Express and `tagify()` raises;
  return a real `ui.output_*` placeholder.
- Making `transform`/`render` sync (`def`) → they must be `async def`; `self.fn`
  is always awaitable.
- Reaching for `output_transformer`/`OutputRenderer` → deprecated; subclass
  `Renderer`. Need the browser to draw a custom payload → author the payload
  here and register the client `OutputBinding` per `references/custom-components.md`.
```
