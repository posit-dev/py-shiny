# Looking up exact signatures with `shiny docs`

## Overview

The `shiny docs` CLI command prints the signature, parameters, types, and
docstring of any Shiny function, class, Playwright controller, or module,
read straight from the installed package's source. Run it before writing an
unfamiliar call instead of guessing argument names; a wrong keyword only
surfaces later as a `TypeError`, or as a controller `AttributeError` in a test.

```bash
shiny docs ui.value_box
```

The `shiny.` prefix is implied, so `ui.value_box` and `shiny.ui.value_box`
are the same lookup. Bare names (`value_box`, `Accordion`) are not resolved;
the error lists the matching paths to pick from.

## What you can look up

```bash
# A UI function: signature line, then the full docstring
shiny docs ui.input_select

# A class: the signature shows its constructor arguments, then its methods
shiny docs render.plot
shiny docs reactive.Value

# A Playwright controller: constructor (page, id), then every expect_*/set method
shiny docs playwright.controller.Accordion

# One method of a controller or class
shiny docs playwright.controller.Accordion.expect_height

# A module: its docstring and the list of public members
shiny docs reactive

# Several at once; errors print first, then the docs separated by ---
shiny docs ui.card ui.value_box playwright.controller.ValueBox
```

Output starts with a Python-style signature line, for example:

```text
def value_box(title: TagChild, value: TagChild, *args: TagChild | TagAttrs, showcase: Optional[TagChild] = None, ..., **kwargs: TagAttrValue) -> Tag:
class Accordion(page: Page, id: str):  # bases: WidthLocM, UiWithContainer
```

## Typos and discovery

A misspelled or incomplete name gets "did you mean" suggestions:

```bash
shiny docs ui.value_bx
# Error: Could not find documentation for 'ui.value_bx'. Did you mean 'ui.value_box'?
```

`--complete` lists every symbol matching a prefix (then substring matches),
which is the quickest way to find a controller's methods or all functions in
an area:

```bash
shiny docs --complete playwright.controller.Accordion.
shiny docs --complete ui.input_
```

Shell tab completion for `bash`, `zsh`, and `fish` uses the same symbol list.

## Machine-readable output

`--json` returns a list of records with `name`, `type` (`function`, `class`,
or `module`), `signature`, `return_type`, `parameters` (each with `name`,
`type`, `default`, `kind`), `docstring`, and for classes `bases` and
`methods`. The list is always valid JSON, empty if every lookup failed; errors
go to stderr and the exit code is 1.

```bash
shiny docs --json ui.card
shiny docs --complete ui.card --json
```

## Mistakes this catches

| Guess | What `shiny docs` shows |
|---|---|
| `ui.value_box(icon=..., color=...)` | `showcase=` holds the icon; `theme=` sets the color |
| `ui.card(title="Sales")` | `card` has no `title`; pass `ui.card_header("Sales")` as a child |
| `controller.get_value()`, `controller.should_be_open()` | controllers expose `expect_value()`, `expect_open()`, `expect_height()`, and `set()` |
| `render.data_frame` as a function call | it is a class whose constructor takes `_fn` and rendering options; configure the table by returning `render.DataGrid(df, selection_mode="rows")` |

## Where to look first

| Area | Example lookups |
|---|---|
| Inputs | `ui.input_select`, `ui.input_slider`, `ui.input_action_button` |
| Cards and layouts | `ui.card`, `ui.layout_columns`, `ui.layout_sidebar`, `ui.value_box` |
| Renderers | `render.text`, `render.plot`, `render.data_frame`, `render.ui` |
| Reactivity | `reactive.calc`, `reactive.effect`, `reactive.event`, `reactive.value` |
| Test controllers | `playwright.controller.InputSlider`, `playwright.controller.ValueBox` |
