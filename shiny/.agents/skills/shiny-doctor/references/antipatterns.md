# Shiny for Python Antipatterns & Prescriptions

This reference catalogues common bugs, antipatterns, and subtle architectural pitfalls in Shiny for Python, explaining why they fail and providing verified patterns to fix them.

---

## 1. Side Effects in `@reactive.calc`

### Symptom
Unstable state, infinite reactive invalidation loops, or duplicate updates.

### Bad Code
```python
@reactive.calc
def filtered_data():
    df = load_data()
    # BAD: mutating reactive state inside a calculation!
    row_count.set(len(df))
    return df[df["score"] > input.threshold()]
```

### Why It Fails
`@reactive.calc` expressions are pure, memoized computations. Calling `.set()` inside a calc produces side effects during the reactive calculation phase, violating the pure functional contract and potentially triggering infinite reactive cycles.

### Good Code
```python
@reactive.calc
def filtered_data():
    df = load_data()
    return df[df["score"] > input.threshold()]

@render.text
def summary():
    return f"Total rows: {len(filtered_data())}"
```

---

## 2. Uncalled Reactive Functions

### Symptom
Outputs render as `<function ... at 0x...>` or expressions silently evaluate to truthy function objects instead of their underlying values.

### Bad Code
```python
@reactive.calc
def total_cost():
    return input.price() * input.quantity()

@render.text
def display():
    # BAD: total_cost is a function/callable, missing parentheses!
    return f"Total: ${total_cost}"
```

### Why It Fails
In Python, `@reactive.calc` and `reactive.value` objects are callables. Referencing them without `()` returns the callable object rather than invoking it to establish the reactive dependency and obtain the value.

### Good Code
```python
@render.text
def display():
    return f"Total: ${total_cost():,.2f}"
```

---

## 3. Reading Reactives Outside Reactive Context

### Symptom
`SilentException`, `RuntimeError: No reactive context available`, or empty static initializations.

### Bad Code
```python
# BAD: reading input or reactive value at top-level module scope
app_ui = ui.page_fluid(
    ui.input_slider("n", "N", 1, 100, 50),
    ui.output_text("txt")
)
# Top-level execution fails or captures static initial value once:
initial_val = input.n()
```

### Why It Fails
Reactive sources can only be read inside reactive contexts (`@reactive.calc`, `@reactive.effect`, `@render.*`, or `with reactive.isolate():`). Outside these contexts, no dependency tracking can occur.

### Good Code
```python
app_ui = ui.page_fluid(
    ui.input_slider("n", "N", 1, 100, 50),
    ui.output_text("txt")
)

def server(input, output, session):
    @render.text
    def txt():
        return f"Current slider: {input.n()}"

app = App(app_ui, server)
```

---

## 4. In-Place Mutation of Reactive Values

### Symptom
Modifying a list or dictionary stored in a `reactive.value` does not trigger dependent outputs or calculations to update.

### Bad Code
```python
items = reactive.value([])

@reactive.effect
@reactive.event(input.add_btn)
def _():
    # BAD: mutating the list in-place does not trigger invalidation!
    items().append(input.new_item())
```

### Why It Fails
Shiny tracks value invalidations when `.set()` is called or when the reactive value is assigned a new reference. Mutating a container in-place does not signal changes to downstream consumers.

### Good Code
```python
items = reactive.value([])

@reactive.effect
@reactive.event(input.add_btn)
def _():
    current = list(items())
    current.append(input.new_item())
    items.set(current)
```

---

## 5. Global State Leakage Across Sessions

### Symptom
One user's actions affect or overwrite another user's session data in multi-user deployments.

### Bad Code
```python
# BAD: Global reactive value at module scope shared across all connections
user_state = reactive.value({"logged_in": False})

def server(input, output, session):
    @reactive.effect
    @reactive.event(input.login)
    def _():
        user_state.set({"logged_in": True, "user": input.username()})
```

### Why It Fails
Module-level variables persist across the entire Python process. When multiple users connect, they share the same global reactive value, causing severe security, privacy, and data corruption bugs.

### Good Code
```python
def server(input, output, session):
    # GOOD: Per-session state initialized inside the server function
    user_state = reactive.value({"logged_in": False})

    @reactive.effect
    @reactive.event(input.login)
    def _():
        user_state.set({"logged_in": True, "user": input.username()})
```

---

## 6. Blocking the Async Event Loop

### Symptom
The whole application stops responding for all connected users during a computation or download.

### Bad Code
```python
import time
import requests

@render.text
def report():
    # BAD: synchronous sleep or requests block the asyncio thread!
    time.sleep(5)
    resp = requests.get("https://api.example.com/data")
    return resp.text
```

### Why It Fails
Shiny runs on an asynchronous event loop. Synchronous blocking calls prevent the event loop from processing WebSocket frames, ping/heartbeat checks, and UI rendering for any session.

### Good Code
```python
import asyncio
import httpx

@render.text
async def report():
    await asyncio.sleep(5)
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.example.com/data")
        return resp.text
```

For long CPU-bound synchronous calculations, use `@reactive.extended_task`:
```python
@reactive.extended_task
async def compute_heavy_task(n: int):
    # Runs in a background worker pool
    import time
    time.sleep(10)
    return n * 42
```

---

## 7. Mismatched UI and Server IDs

### Symptom
Output area in browser remains blank or silently unpopulated without explicit Python traceback.

### Bad Code
```python
app_ui = ui.page_fluid(
    ui.output_text_verbatim("summary_output")
)

def server(input, output, session):
    # BAD: Function name 'summary_text' does NOT match UI ID 'summary_output'
    @render.text
    def summary_text():
        return "Calculation finished."
```

### Why It Fails
In Shiny Core mode, the `@render.*` decorator registers the output using the exact name of the Python function. If this name does not match the UI output placeholder ID, Shiny cannot connect the renderer to the DOM element.

### Good Code
```python
app_ui = ui.page_fluid(
    ui.output_text_verbatim("summary_output")
)

def server(input, output, session):
    @render.text
    def summary_output():
        return "Calculation finished."
```

---

## 8. Duplicate Element IDs

### Symptom
Inputs behave erratically, input values override each other, or outputs overwrite DOM containers.

### Bad Code
```python
app_ui = ui.page_fluid(
    ui.input_text("query", "Search Products"),
    ui.input_text("query", "Search Customers"),  # BAD: Duplicate ID "query"
)
```

### Why It Fails
HTML element IDs and Shiny input/output keys must be unique within their namespace. Duplicates lead to non-deterministic WebSocket event collisions.

### Good Code
```python
app_ui = ui.page_fluid(
    ui.input_text("product_query", "Search Products"),
    ui.input_text("customer_query", "Search Customers"),
)
```

---

## 9. Module Namespace Omission

### Symptom
Module inputs or outputs fail to update or throw `KeyError` when invoked multiple times.

### Bad Code
```python
from shiny import module, ui, render

@module.ui
def counter_ui():
    # BAD: missing ns() wrapper on IDs inside module UI!
    return ui.div(
        ui.input_action_button("btn", "Increment"),
        ui.output_text("val"),
    )
```

### Why It Fails
Without namespacing (`ns("btn")`), multiple instances of `counter_ui()` generate identical HTML IDs, breaking isolation.

### Good Code
```python
from shiny import module, ui, render

@module.ui
def counter_ui():
    # GOOD: session.ns (or ns) automatically scopes IDs to this module instance
    return ui.div(
        ui.input_action_button("btn", "Increment"),
        ui.output_text("val"),
    )

@module.server
def counter_server(input, output, session):
    count = reactive.value(0)

    @reactive.effect
    @reactive.event(input.btn)
    def _():
        count.set(count() + 1)

    @render.text
    def val():
        return f"Count: {count()}"
```

---

## 10. Mixing Express and Core Paradigms

### Symptom
Duplicate UI rendering, layout distortion, or `AttributeError` on `shiny.express` imports.

### Bad Code
```python
from shiny.express import ui
from shiny import App, ui as core_ui

# BAD: Defining explicit App() and app_ui inside a Shiny Express file
app_ui = core_ui.page_fluid(
    ui.h2("Title")
)

def server(input, output, session):
    pass

app = App(app_ui, server)
```

### Why It Fails
Shiny Express apps evaluate top-level code directly into the UI tree and wrap server execution automatically. Instantiating `App(app_ui, server)` within an Express app conflicts with Express's runtime execution model.

### Good Code (Express Mode)
```python
from shiny.express import ui, render, input

ui.page_opts(title="My Express App")
ui.h2("Title")
ui.input_slider("n", "N", 1, 10, 5)

@render.text
def txt():
    return f"Value: {input.n()}"
```

---

## 11. R Shiny Syntax Leakage

### Symptom
`NameError: name 'shinyApp' is not defined` or `NameError: name 'reactiveVal' is not defined`.

### Common R -> Python Equivalents

| R Shiny | Python Shiny Equivalent |
|---|---|
| `shinyApp(ui, server)` | `app = App(app_ui, server)` (Core) or top-level file (Express) |
| `fluidPage(...)` | `ui.page_fluid(...)` |
| `reactiveVal(0)` | `reactive.value(0)` |
| `reactiveValues(...)` | Python dictionary / per-session dataclass / `reactive.value()` |
| `observeEvent(input$btn, { ... })` | `@reactive.effect` + `@reactive.event(input.btn)` |
| `renderPlot({ plot(...) })` | `@render.plot` with `def plot_fn(): ...` |
| `renderUI({ ... })` | `@render.ui` with `def ui_fn(): ...` |
| `req(input$x)` | `req(input.x())` |
| `isolate(input$x)` | `with reactive.isolate(): input.x()` |
| `input$x` / `output$y` | `input.x()` / `@render.* def y():` |
