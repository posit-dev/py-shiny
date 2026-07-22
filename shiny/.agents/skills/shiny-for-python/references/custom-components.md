
# Custom JavaScript components in Shiny for Python

## Overview

Shiny apps talk to the browser over a WebSocket. Instead of hand-wiring that
channel, register your JavaScript with Shiny's client-side registries
(`Shiny.inputBindings`, `Shiny.outputBindings`) or its message bus
(`Shiny.addCustomMessageHandler`). Shiny then handles serialization, initial
values, reconnects, and namespacing for you.

Do NOT reach into `#id` elements from stray `<script>` tags, poll the DOM, or
open your own socket. Ship assets through an `HTMLDependency` (never a bare
`<script src>` pointing outside the app) so ordering and deduplication work. For
pure-Python dynamic UI see `references/dynamic-ui.md`; to wrap an existing Jupyter
widget use shinywidgets (external) rather than writing a binding by hand.

## Ship a component's JS/CSS

Put files in a `www/` folder and register them as one dependency. Attaching the
dependency to any `Tag` (or returning it from the UI) injects the assets once,
in order.

```python
from pathlib import Path
from htmltools import HTMLDependency
from shiny import ui

my_dep = HTMLDependency(
    "my-widget",          # unique name
    "1.0.0",              # version (used for dedup)
    source={"subdir": str(Path(__file__).parent / "www")},
    script={"src": "my-widget.js"},        # or {"src": "index.js", "type": "module"}
    stylesheet={"href": "my-widget.css"},
)

app_ui = ui.page_fluid(
    my_dep,
    ui.div(id="clock", class_="my-widget"),
)
```

## Custom input

Give the element an `id`, then tell Shiny its value with
`Shiny.setInputValue("id", value)`. The server reads it as `input.id()`.

```js
// www/my-widget.js
const el = document.getElementById("counter");
let n = 0;
el.addEventListener("click", () => {
  n += 1;
  Shiny.setInputValue("counter", n);   // id must match input.counter()
});
```

For a reusable element type, register an input binding so Shiny finds every
instance, restores values, and namespaces ids inside modules:

```js
class CounterBinding extends Shiny.InputBinding {
  find(scope) { return scope.querySelectorAll(".my-counter"); }
  getValue(el) { return Number(el.dataset.value || 0); }
  subscribe(el, callback) {
    el.addEventListener("click", () => callback(true));  // callback() -> re-read getValue
  }
  unsubscribe(el) { el.replaceWith(el.cloneNode(true)); }
}
Shiny.inputBindings.register(new CounterBinding(), "my.counter");
```

Read it on the server like any input: `input.counter()`. Pass `resolve_id(id)`
(from `shiny.module`) when building the UI so bindings work inside modules.

## Custom output

Emit an output placeholder, then register an output binding whose
`renderValue(el, data)` receives whatever the server's renderer returns.

```python
# server
from shiny import render
@render.text          # or a custom Renderer; payload must be JSON-serializable
def clock():
    return time.strftime("%H:%M:%S")
```

```js
class ClockBinding extends Shiny.OutputBinding {
  find(scope) { return scope.querySelectorAll(".my-clock"); }
  renderValue(el, data) { el.textContent = data; }   // data = server payload
}
Shiny.outputBindings.register(new ClockBinding(), "my.clock");
```

The placeholder element's `id` must match the render function name; give it the
class your `find()` selects (e.g. `ui.div(id="clock", class_="my-clock")`).

## Server to client messages

For updates that are not tied to an output, push a typed message and handle it
in JS. This is the general server-initiated channel.

```python
# server
@reactive.effect
@reactive.event(input.go)
async def _():
    await session.send_custom_message("flash", {"text": "hi"})
```

```js
Shiny.addCustomMessageHandler("flash", (msg) => {   // type must match
  document.getElementById("banner").textContent = msg.text;
});
```

`send_custom_message` is async - `await` it (or call from an async effect). To
run code right before/after values are sent to the client, use
`@session.on_flush` / `@session.on_flushed` (see `references/session-lifecycle.md`).

## Quick reference

| Need | Python | JavaScript |
|---|---|---|
| Ship JS/CSS | `HTMLDependency(name, ver, source=..., script=..., stylesheet=...)` | files in `www/` |
| Read a value from JS | `input.id()` | `Shiny.setInputValue("id", value)` |
| Reusable input type | UI tag with `id`/class | `Shiny.inputBindings.register(new Shiny.InputBinding(), "ns.name")` |
| Push to an output | `@render.*` returning JSON | `Shiny.outputBindings.register(new Shiny.OutputBinding(), "ns.name")` |
| One-off server->client | `await session.send_custom_message(type, msg)` | `Shiny.addCustomMessageHandler(type, fn)` |
| Namespace ids (modules) | `resolve_id(id)` | handled by binding `find()` |

## Common mistakes

- Bare `<script src>` or CDN tag instead of an `HTMLDependency` -> assets load
  out of order or twice, and break inside modules. Always use a dependency.
- Output placeholder `id` or class doesn't match the render name / binding
  `find()` -> `renderValue` never fires. Keep id == function name and class ==
  selector.
- `send_custom_message` called without `await` -> message never sent (it
  returns a coroutine). Await it in an async effect.
- Message `type` / handler name mismatch -> silently dropped. They must be
  identical strings.
- Hardcoded ids inside a module -> collisions. Wrap ids with `resolve_id()`;
  input/output bindings namespace automatically via `find()`.
- Reading `input.id()` before JS has ever called `setInputValue` -> value is
  `None`; guard with `req(input.id())` (see `references/reactivity.md`).
- Need a build step (TypeScript, Lit, React)? Start from the `shiny create`
  custom-component templates rather than hand-rolling the toolchain.
```
