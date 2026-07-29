# Testing Shiny for Python apps with Playwright

## Overview

shiny ships typed **Playwright controllers** (`shiny.playwright.controller`)
that know each component's DOM structure, plus pytest fixtures that launch the
app in a subprocess. Use them instead of hand-written CSS selectors, raw
locators, or `time.sleep()` — controller `expect_*` methods auto-wait and
auto-retry.

## Setup

```bash
uv pip install pytest playwright pytest-playwright
playwright install chromium
```

Installing shiny registers a pytest plugin, so the `local_app` fixture below
is available without any conftest.

## Write a test

With `app.py` and the test file in the same directory:

```python
# app.py
from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("n", "N", 0, 100, 20),
    ui.output_text_verbatim("txt"),
)

def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def txt():
        return f"n*2 is {input.n() * 2}"

app = App(app_ui, server)
```

```python
# test_app.py
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc

def test_doubles_slider_value(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    slider = controller.InputSlider(page, "n")
    txt = controller.OutputTextVerbatim(page, "txt")

    slider.expect_value("20")
    txt.expect_value("n*2 is 40")

    slider.set("50")
    txt.expect_value("n*2 is 100")
```

Run with `pytest test_app.py`. The `page` fixture comes from
pytest-playwright; `local_app` starts `app.py` from the test file's directory
(in test mode, `SHINY_TESTMODE=1`) and exposes the server's URL as `.url`.

The pattern is always: construct a controller with the component's **id**,
drive it with `.set()` / `.click()`, and assert with `.expect_*()` methods.

## Test an app in another location

```python
from shiny.pytest import create_app_fixture

# Path is relative to this test file. A list of paths parametrizes the tests.
app = create_app_fixture("../apps/dashboard/app.py")

def test_dashboard(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)
    ...
```

`create_app_fixture(app, scope="module", timeout_secs=30, env=None)` — `env`
is merged over the parent environment and defaults to
`{"SHINY_TESTMODE": "1"}`.

## Find the right controller

Controller names follow the UI function: `ui.input_slider` →
`controller.InputSlider`, `ui.output_data_frame` →
`controller.OutputDataFrame`, `ui.card` → `controller.Card`.

| Category | Controllers |
|---|---|
| Inputs | `InputActionButton`, `InputActionLink`, `InputBookmarkButton`, `InputCheckbox`, `InputCheckboxGroup`, `InputCodeEditor`, `InputDarkMode`, `InputDate`, `InputDateRange`, `InputFile`, `InputNumeric`, `InputPassword`, `InputRadioButtons`, `InputSelect`, `InputSelectize`, `InputSlider`, `InputSliderRange`, `InputSubmitTextarea`, `InputSwitch`, `InputTaskButton`, `InputText`, `InputTextArea` |
| Outputs | `OutputCode`, `OutputDataFrame`, `OutputImage`, `OutputPlot`, `OutputTable`, `OutputText`, `OutputTextVerbatim`, `OutputUi` |
| Downloads | `DownloadButton`, `DownloadLink` |
| Containers | `Accordion`, `AccordionPanel`, `Card`, `ValueBox`, `Sidebar`, `Offcanvas`, `Popover`, `Tooltip`, `Toast`, `Chat`, `ToolbarInputButton`, `ToolbarInputSelect` |
| Navigation | `NavPanel`, `NavsetBar`, `NavsetCardPill`, `NavsetCardTab`, `NavsetCardUnderline`, `NavsetHidden`, `NavsetPill`, `NavsetPillList`, `NavsetTab`, `NavsetUnderline`, `PageNavbar` |
| Server state | `AppTestValues` |

## Client-side vs server-side values

Component controllers and `AppTestValues` read from different places, and the
"same" value can legitimately differ between them:

- **Controllers read the browser DOM** — what the user sees. `expect_value()` /
  `get_value()` inspect the rendered widget, so values are strings formatted
  for display: a slider reads `"50"` (or `"1,000"` with a thousands separator),
  a date input reads the displayed date text, an output reads its rendered
  text/HTML.
- **`controller.AppTestValues(page)` reads the server's snapshot** — the
  Python values the server function currently holds: `input.n()` as the int
  `50`, an output as the render function's return value, plus `export` values
  (internal reactives surfaced with `export_test_values()`) that have no DOM
  presence at all.

They can also differ in *time*: the DOM updates instantly when the user
interacts, but the server only sees the change after the websocket round-trip
(and any debounce/throttle), so a client-side value can briefly be ahead of
its server-side counterpart.

Prefer controllers for user-visible behavior; reach for `AppTestValues` when
asserting server state:

```python
app_values = controller.AppTestValues(page)
app_values.expect_input("n", 50)          # server-side: int, not "50"
app_values.expect_export("doubled", 100)  # internal reactive, no DOM
app_values.expect_input("n", is_integer)  # predicate: any callable(actual) -> bool
```

Expected values may be predicates (callables taking the actual value, retried
until truthy). Use named functions, not lambdas — the function's name appears
in failure messages.

See `references/debugging.md` for the full test-mode snapshot API.

## Debug a failing test

```bash
pytest test_app.py --headed                    # watch the browser
pytest test_app.py --tracing retain-on-failure # then: playwright show-trace <trace.zip>
```

## Generate a test with AI

`shiny add test --app app.py` analyzes an app and writes a test file for it
(requires `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY` with `--provider openai`).

## Common mistakes

- Test times out with a blank page → you forgot `page.goto(local_app.url)`.
- Flaky assertions → replace `time.sleep()` + plain `assert` with the
  controller's auto-waiting `expect_*()` methods.
- Controller "not found" for a component inside a module → ids are
  namespaced: `controller.InputText(page, "mymodule-txt")`.
- `local_app` fails to start → it only launches a file named `app.py` next to
  the test file; for any other name or location use `create_app_fixture()`.
- `ImportError` from `shiny.playwright` → install `playwright` (and
  `pytest-playwright` when running under pytest).
