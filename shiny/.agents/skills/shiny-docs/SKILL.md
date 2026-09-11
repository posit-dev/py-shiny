---
name: shiny-docs
description: "Inspect exact Shiny for Python component signatures, parameters, types, test controllers, and docstrings using the `shiny docs` CLI command (`shiny docs <name>`, `shiny docs --json <name>`, `shiny docs --complete <prefix>`). Use whenever writing or modifying Shiny UI components, reactive server logic, or Playwright controller tests and you need exact argument names, defaults, return types, or controller assertions without guessing."
---

# Shiny Documentation Lookup (`shiny docs`)

The `shiny docs` CLI command lets you inspect accurate, AST-extracted signatures, parameters, types, test controllers, and docstrings directly in your workspace.

Always run `shiny docs` before writing unfamiliar Shiny components or Playwright controller tests to avoid argument hallucinations or runtime `TypeError`/`AttributeError`.

---

## 1. Quick Usage

```bash
# Inspect a UI component (shiny. is implied)
shiny docs ui.value_box

# Inspect with explicit full path
shiny docs shiny.ui.card

# Inspect a Playwright test controller
shiny docs playwright.controller.Accordion

# Inspect a specific test controller method
shiny docs playwright.controller.Accordion.expect_height

# Inspect reactive or rendering helpers
shiny docs reactive.calc
shiny docs render.data_frame

# Inspect multiple items in one call (errors shown first)
shiny docs ui.card ui.value_box playwright.controller.ValueBox
```

---

## 2. Programmatic & Machine-Readable Output (`--json`)

When you need structured JSON data containing exact parameters, type annotations, defaults, return types, and docstrings:

```bash
shiny docs --json ui.value_box
```

---

## 3. Autocomplete & Symbol Discovery (`--complete`)

To discover available methods, classes, or functions matching a prefix:

```bash
# Discover all methods on Accordion controller
shiny docs --complete playwright.controller.Accordion.

# Discover all value box utilities
shiny docs --complete ui.value_box
```

---

## 4. Key Shiny Components Reference Map

| Area | Module Path | Example Command |
|---|---|---|
| Value Boxes | `ui.value_box`, `ui.value_box_theme` | `shiny docs ui.value_box` |
| Cards & Layouts | `ui.card`, `ui.layout_columns`, `ui.layout_sidebar` | `shiny docs ui.card` |
| Accordions | `ui.accordion`, `ui.accordion_panel` | `shiny docs ui.accordion` |
| Inputs | `ui.input_select`, `ui.input_slider`, `ui.input_action_button` | `shiny docs ui.input_select` |
| Renderers | `render.text`, `render.plot`, `render.data_frame`, `render.ui` | `shiny docs render.data_frame` |
| Reactivity | `reactive.calc`, `reactive.effect`, `reactive.event`, `reactive.value` | `shiny docs reactive.calc` |
| Test Controllers | `playwright.controller.ValueBox`, `playwright.controller.Accordion`, etc. | `shiny docs playwright.controller.ValueBox` |

---

## 5. Common Hallucinations Avoided by `shiny docs`

1. **`ui.value_box` arguments**:
   - ❌ `icon=...`, `color=...` (from R Shiny or other frameworks)
   - ✅ `showcase=...`, `theme=...` (exact Py-Shiny arguments)
2. **`playwright.controller` assertions**:
   - ❌ `controller.get_value()`, `controller.should_be_open()`
   - ✅ `controller.expect_value()`, `controller.expect_open()`, `controller.expect_height()`
3. **`render.data_frame` options**:
   - ❌ `render.data_frame(grid=True)`
   - ✅ `render.DataGrid(df, selection_mode="rows")` or `render.DataTable(df)`
