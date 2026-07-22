# Layouts in Shiny for Python (Core)

## Overview

Build page structure by composing bslib layout functions from `shiny.ui`, not by
hand-writing Bootstrap `<div class="row">`/`col-*` markup or raw CSS flexbox.
Every app starts with one page function that sets the container and (optionally)
a filling body; inside it you nest `card()`, `layout_columns()`,
`layout_sidebar()`, `value_box()`, and `accordion()`. These containers are
responsive and theme-aware for free.

This reference documents the Core (function-call) form, e.g. `ui.card(...)`. For the
Express context-manager form (`with ui.card():`) see `references/express.md`.

## Choose a page function

Every app_ui is wrapped in exactly one page function:

```python
from shiny import App, ui

app_ui = ui.page_sidebar(          # sidebar + main area (most dashboards)
    ui.sidebar("Controls go here", title="Filters"),
    ui.card("Main content"),
    title="My Dashboard",
)
app = App(app_ui, None)
```

- `page_sidebar(sidebar, *args)` — dashboard with a left sidebar and a title.
- `page_fillable(*args)` — body fills the viewport height; children flex to fit.
  Best for full-window dashboards with no scrolling.
- `page_fluid(*args)` — full-width flowing document; content scrolls normally.
- `page_fixed(*args)` — like fluid but capped at Bootstrap's max container width.

## Group content in a card

`card()` is the standard content box. `card_header()` / `card_footer()` are
optional and must be direct children. `full_screen=True` adds an expand button.

```python
ui.card(
    ui.card_header("Sales"),
    ui.output_plot("sales_plot"),
    ui.card_footer("Updated hourly"),
    full_screen=True,
)
```

## Arrange cards in a grid: `layout_columns`

`layout_columns()` uses a responsive 12-column grid. `col_widths` sets each
child's width in grid units (out of 12); values wrap to the next row past 12,
and a dict sets widths per breakpoint (`sm`, `md`, `lg`, ...).

```python
ui.layout_columns(
    ui.card("A"),
    ui.card("B"),
    ui.card("C"),
    col_widths={"sm": (12,), "lg": (4, 4, 4)},  # stacked on mobile, 3-up on large
    row_heights=(1, 2),
)
```

## Equal-size tiles: `layout_column_wrap`

When every item should be the same width, use `layout_column_wrap()`. `width`
is a fraction (`1/2` = two per row) or a CSS width (`"250px"` = as many as fit).

```python
ui.layout_column_wrap(
    ui.card("one"), ui.card("two"), ui.card("three"), ui.card("four"),
    width=1 / 2,
)
```

## Sidebar inside a card or region: `layout_sidebar`

Use `page_sidebar` for a page-level sidebar; use `layout_sidebar()` to put a
sidebar inside a card or any region. Give `sidebar()` an `id` to read its
open/closed state as `input.<id>()`.

```python
ui.card(
    ui.layout_sidebar(
        ui.sidebar("Options", id="opts", open="desktop", position="left"),
        ui.output_plot("plot"),
    ),
)
```

## KPI tiles: `value_box`

```python
ui.value_box(
    "Total revenue",              # title
    "$1.2M",                      # value
    "Up 30% vs last month",       # optional supporting text
    showcase=ui.tags.i(class_="bi bi-cash"),
    theme="bg-gradient-orange-red",
)
```

## Collapsible sections: `accordion`

```python
ui.accordion(
    ui.accordion_panel("Section A", "Content A"),
    ui.accordion_panel("Section B", "Content B"),
    id="acc",              # optional: read open panels via input.acc()
    open="Section A",      # False = all closed, True = all open, or panel name(s)
    multiple=True,
)
```

## Quick reference

| Need | Use |
|---|---|
| Page with sidebar + title | `ui.page_sidebar(ui.sidebar(...), ...)` |
| Full-window flexbox page | `ui.page_fillable(...)` |
| Scrolling document page | `ui.page_fluid(...)` / `ui.page_fixed(...)` |
| Content box | `ui.card(ui.card_header(...), ..., full_screen=True)` |
| Responsive 12-col grid | `ui.layout_columns(..., col_widths=(4, 8))` |
| Equal-width wrapping tiles | `ui.layout_column_wrap(..., width=1/2)` |
| Sidebar within a region | `ui.layout_sidebar(ui.sidebar(..., id="s"), ...)` |
| KPI tile | `ui.value_box(title, value, *info)` |
| Collapsible sections | `ui.accordion(ui.accordion_panel(...), ...)` |

## Common mistakes

- **Content won't fill the window / plot is tiny.** Filling needs an unbroken
  chain of fillable containers from the page down. Use `page_fillable()` (or
  `page_sidebar(..., fillable=True)`); `card` and `layout_columns` fill by
  default, but a plain `page_fluid` does not. An output only expands if every
  ancestor fills.
- **Explicit `height=` gets ignored inside a fill container.** A fillable parent
  stretches children to share space. Set `height`/`row_heights` on the
  container, or drop it into a non-filling page.
- **Hand-writing `ui.div(class_="row")` + `col-*`.** Use `layout_columns` /
  `layout_column_wrap`; they are responsive and theme-aware.
- **`card_header`/`card_footer` not rendering as header/footer.** They must be
  direct children of `card()`, not nested inside another element.
- **`input.<id>()` is `None` for a sidebar/accordion.** You must pass an `id=`
  to `sidebar()` / `accordion()` to create the input binding.
- **More than one page function.** An app has exactly one top-level page; nest
  layout containers inside it, don't stack pages.
