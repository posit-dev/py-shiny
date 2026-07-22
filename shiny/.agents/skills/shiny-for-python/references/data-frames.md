# Rendering interactive data frames in Shiny for Python

## Overview

Return a pandas, polars, or eager narwhals `DataFrame` from a
`@render.data_frame`-decorated function paired with a `ui.output_data_frame(id)`
placeholder. Wrap the frame in `render.DataGrid` or `render.DataTable` to set
options. Do **not** hand-build an HTML `<table>` or poll the frame to detect
interaction — selection, sorting, filtering, and edits are all reactive inputs
you read from the renderer object.

```python
from shiny import App, render, ui
import pandas as pd

df = pd.DataFrame({"name": ["a", "b", "c"], "value": [1, 2, 3]})

app_ui = ui.page_fluid(ui.output_data_frame("grid"))

def server(input, output, session):
    @render.data_frame
    def grid():
        return render.DataGrid(df, selection_mode="rows", filters=True)

app = App(app_ui, server)
```

Returning a bare `DataFrame` is shorthand for `render.DataGrid(df)`.

## DataGrid vs DataTable

Identical API; they differ only in browser styling and default height. Use
`DataGrid` for a compact, spreadsheet-like virtualized grid (default
`height=None`, grows to fit / fills its container). Use `DataTable` for a more
document-like table (default `height="500px"`, body scrolls).

## Read the selected rows

Read selection from the renderer inside another reactive. `.cell_selection()`
returns a `CellSelection` dict with `type` (`"none"`/`"row"`/`"col"`/`"rect"`),
`rows`, and `cols`. Simpler: `.data_view(selected=True)` returns the selected
rows as a DataFrame (with sorting/filtering/edits already applied).

```python
@render.data_frame
def grid():
    return render.DataGrid(df, selection_mode="rows")

@render.text
def selected():
    rows = grid.cell_selection()["rows"]   # tuple of row indices
    return f"{len(rows)} rows selected"

@render.data_frame
def subset():
    return render.DataGrid(grid.data_view(selected=True))
```

`selection_mode` is `"none"` (default, not selectable), `"row"` (one row), or
`"rows"` (multiple).

## Read sorted / filtered / edited state

`.data_view()` returns the frame exactly as the user currently sees it — edits
applied, then filtering and sorting. `.data_view_rows()` gives the visible row
indices. `filters=True` shows per-column filter inputs; sorting works by
clicking headers (no option needed).

```python
@render.data_frame
def grid():
    return render.DataGrid(df, filters=True)

@render.text
def visible_count():
    return f"{len(grid.data_view_rows())} rows shown"
```

## Edit cells

Set `editable=True`, then register a patch handler to coerce/persist each edit.
`@<name>.set_patch_fn` handles one cell; `@<name>.set_patches_fn` handles a
batch. A `CellPatch` is a dict with `row_index`, `column_index`, and `value`
(a string as typed); return the processed `CellValue`.

```python
@render.data_frame
def grid():
    return render.DataGrid(df, editable=True)

@grid.set_patch_fn
def _(*, patch: render.CellPatch) -> render.CellValue:
    if patch["column_index"] == 1:
        return int(patch["value"])   # store numeric column as int
    return patch["value"]
```

Read the edited frame with `grid.data_patched()` or `grid.data_view()`.

## Style cells

Pass `styles=` a style-info dict, a list of them, or a function of the frame.
Each entry targets `rows`/`cols` (omit either to mean "all") with a `style`
dict (kebab- or camel-cased CSS) and/or a `class` string.

```python
render.DataGrid(df, styles=[{"cols": [1], "style": {"background-color": "yellow"}}])
```

## Programmatic updates (async)

From an effect, drive the grid: `await grid.update_cell_selection({"type": "row", "rows": [0, 2]})`
(or `"all"` / `None`), `await grid.update_sort([{"col": 1, "desc": True}])`,
`await grid.update_filter(...)`, `await grid.update_data(new_df)` (replaces data,
drops edits, keeps sort/filter), and `await grid.update_cell_value(v, row=0, col="name")`.

## Quick reference

| Item | Options |
|---|---|
| Wrappers | `render.DataGrid` (grid, `height=None`), `render.DataTable` (table, `height="500px"`) |
| `selection_mode` | `"none"`, `"row"`, `"rows"` |
| Key `DataGrid`/`DataTable` args | `width`, `height`, `summary`, `filters`, `editable`, `selection_mode`, `styles` |
| Read state | `.cell_selection()`, `.data_view(selected=...)`, `.data_view_rows()`, `.data_patched()`, `.sort()`, `.filter()` |
| Edit hooks | `@<name>.set_patch_fn`, `@<name>.set_patches_fn` |
| Update (async) | `.update_cell_selection()`, `.update_sort()`, `.update_filter()`, `.update_data()`, `.update_cell_value()` |
| Raw inputs | `input.<id>_cell_selection()`, `input.<id>_data_view_rows()`, `input.<id>_column_sort()`, `input.<id>_column_filter()` |

## Common mistakes

- No rows ever selectable → you left `selection_mode` at its `"none"` default.
- Reading `input.<id>_selected_rows()` → the input is `input.<id>_cell_selection()`; prefer the renderer's `.cell_selection()`.
- Edits do nothing / aren't the right type → set `editable=True` **and** a `set_patch_fn` that returns the coerced value; `patch["value"]` arrives as a string.
- `update_*` raising "not awaited" or silently no-op → these are async; call them with `await` inside a `@reactive.effect`.
- Selection ignored on programmatic update → `.selection_mode` must be `"row"`/`"rows"`; `update_cell_selection` warns and clears under `"none"`.
- Mutating `.data_view()` / `.data()` in place corrupts the source — they are shallow copies; `.copy()` before mutating.
- Need to assert on the grid in a Playwright test → see `references/testing.md` (`controller.OutputDataFrame`).
