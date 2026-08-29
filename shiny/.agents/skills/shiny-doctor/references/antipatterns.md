# Shiny for Python Antipatterns & Prescriptions

This reference catalogues common bugs, antipatterns, and subtle architectural pitfalls in Shiny for Python, explaining why they fail and providing verified patterns to fix them.

---

## 1. Side Effects in `@reactive.calc`

### Symptom
Unstable state, infinite reactive invalidation loops, or duplicate updates.

### Bad Code
```python
from shiny import reactive, render

row_count = reactive.value(0)

@reactive.calc
def filtered_data():
    df = [1, 2, 3]
    # BAD: mutating reactive state inside a calculation!
    row_count.set(len(df))
    return df
```

### Why It Fails
`@reactive.calc` expressions are pure, memoized computations. Calling `.set()` inside a calc produces side effects during the reactive calculation phase, violating the pure functional contract and potentially triggering infinite reactive cycles.

### Good Code
```python
from shiny import reactive, render

@reactive.calc
def filtered_data():
    return [1, 2, 3]

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
from shiny import reactive, render

@reactive.calc
def total_cost():
    return 100

@render.text
def display():
    # BAD: total_cost is a function/callable, missing parentheses!
    return f"Total: ${total_cost}"
```

### Why It Fails
In Python, `@reactive.calc` and `reactive.value` objects are callables. Referencing them without `()` returns the callable object rather than invoking it to establish the reactive dependency and obtain the value.

### Good Code
```python
from shiny import reactive, render

@reactive.calc
def total_cost():
    return 100

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
from shiny import reactive

val = reactive.value(10)

# BAD: reading val() at top-level module scope outside a reactive context raises RuntimeError
initial_val = val()
```

### Why It Fails
Reactive values and calculations can only be read inside a reactive context (`@reactive.calc`, `@reactive.effect`, `@render.*`, or `with reactive.isolate():`). Outside these contexts, no dependency tracking or session scope exists, raising a `RuntimeError`.

### Good Code
```python
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.output_text("txt")
)

def server(input, output, session):
    val = reactive.value(10)

    @render.text
    def txt():
        # GOOD: reactive read inside a renderer context
        return f"Current value: {val()}"

app = App(app_ui, server)
```

---

## 4. In-Place Mutation of Reactive Values

### Symptom
Modifying a list or dictionary stored in a `reactive.value` does not trigger dependent outputs or calculations to update, or causes self-invalidation loops if done in an unconditional effect.

### Bad Code
```python
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("add_btn", "Add Item"),
    ui.output_text("item_count")
)

def server(input, output, session):
    items = reactive.value([])

    @reactive.effect
    @reactive.event(input.add_btn)
    def _():
        # BAD: In-place mutation inside reactive effect does NOT trigger downstream invalidations
        items().append("new_item")

    @render.text
    def item_count():
        return f"Total items: {len(items())}"

app = App(app_ui, server)
```

### Why It Fails
Shiny tracks value invalidations when `.set()` is called or when the reactive value is assigned a new reference. Mutating a container in-place does not signal changes to downstream consumers.

### Good Code
```python
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("add_btn", "Add Item"),
    ui.output_text("item_count")
)

def server(input, output, session):
    items = reactive.value([])

    @reactive.effect
    @reactive.event(input.add_btn)
    def _():
        # GOOD: @reactive.event isolates other reads; assigning a new container or .set() invalidates consumers
        current = list(items())
        current.append("new_item")
        items.set(current)

    @render.text
    def item_count():
        return f"Total items: {len(items())}"

app = App(app_ui, server)
```

---

## 5. Global State Leakage Across Sessions

### Symptom
One user's actions affect or overwrite another user's session data in multi-user deployments.

### Bad Code
```python
from shiny import App, reactive, render, ui

# BAD: Global reactive value at module scope shared across all connections
user_state = reactive.value({"logged_in": False})

def server(input, output, session):
    @render.text
    def status():
        return f"Logged in: {user_state()['logged_in']}"
```

### Why It Fails
Module-level variables persist across the entire Python process. When reactive values at module scope contain user- or session-specific data (such as login state, user preferences, or cart items), multiple concurrent users share and overwrite the same state, causing cross-session leakage. (Note: Global reactive values are valid when cross-session state sharing is explicitly intended, e.g. shared persistent counters or application-wide broadcast channels).

### Good Code
```python
from shiny import App, reactive, render, ui

def server(input, output, session):
    # GOOD: Per-session state initialized inside the server function
    user_state = reactive.value({"logged_in": False})

    @render.text
    def status():
        return f"Logged in: {user_state()['logged_in']}"
```

---

## 6. Blocking the Async Event Loop and Extended Tasks

### Symptom
The application stops responding for all connected users during a computation, download, or sleep, or extended tasks attempt to read reactive values directly.

### Bad Code 1: Blocking call on the event loop
```python
import time
from shiny import render

@render.text
def report():
    # BAD: time.sleep blocks the asyncio event loop thread!
    time.sleep(5)
    return "Done"
```

### Bad Code 2: False belief that `@reactive.extended_task` automatically runs in a thread/process pool
```python
import time
from shiny import reactive

@reactive.extended_task
async def compute_heavy_task(n: int):
    # BAD: ExtendedTask runs on the main thread's event loop!
    # time.sleep(10) STILL freezes the whole server!
    time.sleep(10)
    return n * 42
```

### Bad Code 3: Reading reactive sources directly inside `@reactive.extended_task`
```python
import asyncio
from shiny import reactive

@reactive.extended_task
async def do_work():
    # BAD: Extended tasks cannot access reactive sources directly!
    # input.filename() or reactive values cannot be read inside extended_task.
    filename = "data.csv"
    await asyncio.sleep(1)
    return filename
```

### Why It Fails
Shiny server functions and `@reactive.extended_task` coroutines run on the single asyncio event loop thread. Calling `time.sleep()`, synchronous `requests`, or CPU-bound loops directly inside `async def` blocks the event loop from servicing other WebSocket connections and reactive flushes.

Furthermore, `@reactive.extended_task` executes independently of reactive processing and **cannot directly read reactive sources** (`input.x()`, `reactive.value()`). Because inputs can change while an asynchronous task is executing, Shiny does not track reactive dependencies inside extended tasks. Any reactive values or inputs needed by the task must be passed in as arguments upon invocation.

### Good Code: True async I/O
```python
import asyncio
from shiny import render

@render.text
async def report():
    # GOOD: Non-blocking async sleep yields to the event loop
    await asyncio.sleep(5)
    return "Done"
```

### Good Code: Blocking synchronous I/O offloaded to worker thread with invocation from reactive effect
```python
import asyncio
import time
from shiny import App, reactive, render, ui

def load_file(filename: str) -> str:
    time.sleep(2)
    return f"Loaded {filename}"

app_ui = ui.page_fluid(
    ui.input_text("filename", "File Name", "data.csv"),
    ui.input_action_button("run", "Load"),
    ui.output_text("result"),
)

def server(input, output, session):
    # GOOD: Task accepts needed inputs as parameters and offloads blocking work
    @reactive.extended_task
    async def do_work(filename: str) -> str:
        return await asyncio.to_thread(load_file, filename)

    # GOOD: Reactive effect captures reactive input value and invokes task
    @reactive.effect
    @reactive.event(input.run)
    def _():
        do_work(input.filename())

    # GOOD: Output renderer consumes task result via .result()
    @render.text
    def result():
        return do_work.result()

app = App(app_ui, server)
```

### Good Code: CPU-bound computation offloaded to a ProcessPoolExecutor
```python
import asyncio
from concurrent.futures import ProcessPoolExecutor
from shiny import reactive

process_pool = ProcessPoolExecutor(max_workers=2)

def heavy_cpu_crunch(n: int) -> int:
    total = sum(i * i for i in range(n))
    return total

@reactive.extended_task
async def cpu_task(n: int):
    # GOOD: Offloads heavy CPU calculation to a background process pool
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_pool, heavy_cpu_crunch, n)
```

---

## 7. Mismatched UI and Server IDs

### Symptom
Output area in browser remains blank or silently unpopulated without explicit Python traceback.

### Bad Code
```python
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.output_text_verbatim("summary_output")
)

def server(input, output, session):
    # BAD: Function name 'summary_text' does NOT match UI ID 'summary_output'
    @render.text
    def summary_text():
        return "Calculation finished."

app = App(app_ui, server)
```

### Why It Fails
In Shiny Core mode, the `@render.*` decorator registers the output using the function name by default, or using the ID specified with `@output(id="...")`. If the effective output ID does not match the UI output placeholder ID, Shiny cannot connect the renderer to the DOM element.

### Good Code 1: Matching function name to UI ID
```python
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.output_text_verbatim("summary_output")
)

def server(input, output, session):
    # GOOD: Function name matches UI ID
    @render.text
    def summary_output():
        return "Calculation finished."

app = App(app_ui, server)
```

### Good Code 2: Overriding output ID with `@output(id=...)`
```python
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.output_text_verbatim("summary_output")
)

def server(input, output, session):
    # GOOD: Explicit @output(id=...) overrides function name to match UI ID
    @output(id="summary_output")
    @render.text
    def make_summary():
        return "Calculation finished."

app = App(app_ui, server)
```

---

## 8. Duplicate Element IDs

### Symptom
Inputs behave erratically, input values override each other, or outputs overwrite DOM containers.

### Bad Code
```python
from shiny import ui

app_ui = ui.page_fluid(
    ui.input_text("query", "Search Products"),
    ui.input_text("query", "Search Customers"),  # BAD: Duplicate ID "query"
)
```

### Why It Fails
HTML element IDs and Shiny input/output keys must be unique within their namespace. Duplicates lead to non-deterministic WebSocket event collisions.

### Good Code
```python
from shiny import ui

app_ui = ui.page_fluid(
    ui.input_text("product_query", "Search Products"),
    ui.input_text("customer_query", "Search Customers"),
)
```

---

## 9. Module Instance ID Mismatches and Collisions

### Symptom
Module outputs remain blank, module inputs never update, or two module instances collide.

### Bad Code 1: Mismatched instance ID between UI and Server call
```python
from shiny import App, module, reactive, render, ui

@module.ui
def counter_ui():
    # Note: @module.ui automatically namespaces "btn" and "val"!
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

app_ui = ui.page_fluid(
    counter_ui("counter_a")
)

def server(input, output, session):
    # BAD: Typo in module instance ID ('counter_1' vs 'counter_a')!
    counter_server("counter_1")

app = App(app_ui, server)
```

### Bad Code 2: Duplicate module instance IDs
```python
from shiny import ui

# BAD: Calling counter_ui twice with the same instance ID "counter_a"
app_ui = ui.page_fluid(
    counter_ui("counter_a"),
    counter_ui("counter_a")
)
```

### Why It Fails
In Shiny for Python, `@module.ui` automatically prefixes all inner input and output IDs using the instance ID passed to `counter_ui("id")`. If the server module is called with a different instance ID (`counter_server("different_id")`), the server listens on a completely different namespace than the UI rendered.

### Good Code
```python
from shiny import App, module, reactive, render, ui

@module.ui
def counter_ui():
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

app_ui = ui.page_fluid(
    counter_ui("counter_1"),
    counter_ui("counter_2")
)

def server(input, output, session):
    counter_server("counter_1")
    counter_server("counter_2")

app = App(app_ui, server)
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
from shiny.express import input, render, ui

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
