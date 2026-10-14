---
title: "Data Frame Rendering"
description: "How render.data_frame works end to end: narwhals data handling, DataGrid/DataTable payloads, the React client, cell editing via patches, selection/sort/filter inputs, styles, and tests. Read before changing anything under shiny/render/_data_frame*.py or js/data-frame/."
---

# Data Frame Rendering

`@render.data_frame` turns a pandas/polars/narwhals frame into an interactive
virtualized grid (TanStack Table + React). Sorting and filtering happen in the
browser; the server learns about them through inputs. Edits round-trip through a
request handler so the app can validate/coerce values.

## Files

| Area | Location |
|---|---|
| Renderer | `shiny/render/_data_frame.py` (`data_frame`, `assert_column_filters`) |
| Options wrappers | `shiny/render/_data_frame_utils/_datagridtable.py` (`DataGrid`, `DataTable`) |
| Narwhals helpers | `_data_frame_utils/_tbl_data.py` (`as_data_frame`, `serialize_frame`, `serialize_dtype`, `apply_frame_patches`, `subset_frame`, `as_col_indexes`) |
| Wire types | `_data_frame_utils/_types.py` (`FrameRender`, `FrameJson`, `CellPatch`, `ColumnSort`, `ColumnFilter`, `StyleInfo`, `CellValue`) |
| Selection | `_data_frame_utils/_selection.py` (`SelectionModes`, `as_selection_modes`, `as_cell_selection`) |
| Styles | `_data_frame_utils/_styles.py` (`as_style_infos`, `as_browser_style_infos`) |
| HTML cells | `_data_frame_utils/_html.py` (`maybe_as_cell_html`, `series_contains_htmltoolslike`) |
| Per-instance calcs | `_data_frame_utils/_reactive_method.py` (`reactive_calc_method`) |
| Output UI | `shiny/ui/dataframe/_data_frame.py` (`output_data_frame` -> `<shiny-data-frame>` + `data_frame_deps()`) |
| Client | `js/data-frame/` (`index.tsx`, `cell.tsx`, `data-update.tsx`, `selection.tsx`, `sort.ts`, `filter*.tsx`, `style-info.ts`, `request.ts`) built by `js/build.ts` to `shiny/www/py-shiny/data-frame/data-frame.js` |
| Examples | `shiny/api-examples/data_frame*/` |

Public exports in `shiny/render/__init__.py`: `data_frame`, `DataGrid`,
`DataTable`, `CellPatch`, `CellSelection`, `StyleInfo`.

## Render -> payload -> client

1. `data_frame.render()` first calls `_reset_reactives()` (clears `_value`,
   `_cell_patch_map`, `_updated_data`) and unregisters the patch handler, so
   **every re-render wipes edits, sort, filter, and selection**.
2. A bare frame is wrapped as `DataGrid(value)`; `None` renders nothing.
3. `_set_patches_handler()` registers `_patches_handler` via
   `session.set_message_handler(f"data_frame_patches_{output_id}", ...)` (the
   session namespaces it inside modules); the returned key is sent as
   `patchInfo.key`.
4. `value.to_payload()` runs inside `session_context()` and returns `FrameJson`:
   `serialize_frame()` output (`columns`, row-major `data`, `typeHints`,
   `htmlDeps`) plus `options` (`width`, `height`, `summary`, `filters`,
   `editable`, `style: "grid" | "table"`, `styles`; `DataGrid` also sends
   `fill = height is None`). Final shape is `FrameRender`:
   `{payload, patchInfo, selectionModes}`.
5. Client: `ShinyDataFrameOutputBinding` (registered as `"shinyDataFrame"`)
   calls `ShinyDataFrameOutput.renderValue()`, which mounts `<ShinyDataGrid>`
   in a React root. Column ids are positional (`columnIndexToId` /
   `columnIdToIndex` in `index.tsx`), never names.

Serialization details (`serialize_frame`, `serialize_dtype`):
- Type hints come from narwhals dtypes: `string`, `numeric`, `categorical`
  (+ `categories`), `boolean`, `date`, `datetime`, `duration`, `time`, `binary`,
  `object`, `unknown`, `html`. `object`/`unknown` become `html` if
  `series_contains_htmltoolslike()` finds a tag node in the first ~1000 values.
- Rows go through `orjson` with a `default=` hook: tag nodes are rendered with
  `session._process_ui()` into `CellHtml` (`{"isShinyHtml": true, "obj": ...}`)
  with deps stripped and collected into deduped `htmlDeps`; **any other
  non-JSON value becomes `str(val)`**.
- The client renders `CellHtml` with `Shiny.renderContentAsync` and
  `unbindAll`s on cleanup (`cell.tsx`). HTML columns have sorting disabled and
  are not editable.

## Server -> client updates

All go through `_send_message_to_browser()` as custom message
`shinyDataFrameMessage` `{id: session.ns(output_id), handler, obj}`; the JS shim
at the bottom of `index.tsx` re-dispatches it as a DOM `CustomEvent` named
`handler` on the element.

| Python method | Handler | Notes |
|---|---|---|
| `update_cell_value(value, row=, col=)` | `addPatches` | Adds to `_cell_patch_map`; keeps sort/filter. `col` may be a name. |
| `update_data(data)` | `updateData` | Sets `_updated_data`, clears patches. Client remaps sort/filter by column *name* and drops ones that no longer apply. |
| `update_cell_selection(sel)` | `updateCellSelection` | Only `row` selections; `"all"`/`None` accepted. Warns and clears if mode is `none`. |
| `update_sort(sort)` | `updateColumnSort` | Bare `int` upgrades to `{"col", "desc": dtype.is_numeric()}`. |
| `update_filter(filter)` | `updateColumnFilter` | Validated by `assert_column_filters`. |
| (effect) `_attempt_update_cell_style()` | `updateStyles` | Re-runs a callable `styles=` on `data_patched()` whenever patches or `_updated_data` change (`ignore_init=True`). |

## Editing (patches)

- Enabled by `DataGrid/DataTable(editable=True)`. Double-click a non-HTML cell
  to edit; the browser always sends the edited value as a **string**.
- `updateCellsData()` (`data-update.tsx`) calls `makeRequestPromise({method:
  patchInfo.key, args: [patches]})` with `{row_index, column_index, value}`.
- `_patches_handler()` -> `assert_patches_shape` -> `self._patches_fn(patches=)`
  -> `_set_cell_patch_map_patches()` (keyed `(row, col)`, last write wins) ->
  returns processed patches (HTML upgraded via `maybe_as_cell_html`). The
  client applies whatever comes back, so `patches_fn` may return fewer, more,
  or different cells. A raised exception marks the cells `EditFailure` with the
  error as the cell title.
- Defaults (`_init_patch_fns`): `patch_fn` returns `patch["value"]` unchanged;
  `patches_fn` calls `_patch_fn` per patch. Override with
  `@<renderer>.set_patch_fn` / `@<renderer>.set_patches_fn` (sync or async,
  wrapped by `wrap_async`; keyword-only `patch=` / `patches=`). They return
  `None`, deliberately, so Express doesn't register them twice.
- Return values must be `CellValue` = `TagNode | str | int | float | bool | None`
  (JSON scalars only; e.g. a `datetime` fails when sent back).

## Reactive data methods

Built with `@reactive_calc_method`, which lazily creates one `reactive.calc`
per renderer instance (cached in a `WeakKeyDictionary` and pinned on
`self.__dict__`).

- `data()` - `_updated_data` if set, else the rendered `.data`.
- `cell_patches()` -> `data_patched()` (`apply_frame_patches`: clone, group by
  column index, `nw_data[:, i].scatter(...)`, `with_columns`).
- `data_view(selected=False)` - `data_patched()` subset to `data_view_rows()`
  (or `cell_selection()["rows"]`); returns the caller's native type
  (`_nw_data_to_original_type`; narwhals in -> narwhals out).
- `cell_selection()`, `data_view_rows()`, `sort()`, `filter()` wrap the inputs
  below. `selection_modes()` reads `DataGrid.selection_modes`.
- `input_cell_selection()` is deprecated.

## Inputs set by the client (`index.tsx`)

| Input | Value | Read by |
|---|---|---|
| `<id>_cell_selection` | `{type: "row", rows: [...]}` or `null` when mode is none | `cell_selection()` -> `as_cell_selection()` fills in `cols`, drops out-of-range indices |
| `<id>_sort` / `<id>_column_sort` (deprecated) | `[{col, desc}]` | `sort()` reads `_column_sort` |
| `<id>_filter` / `<id>_column_filter` (deprecated) | `[{col, value}]`, sorted by `col`; value is a string or `[min, max]` | `filter()` reads `_column_filter` |
| `<id>_data_view_rows` / `<id>_data_view_indices` (legacy) | original row indices after sort+filter | `data_view_rows()` |
| `<id>_selected_rows` (legacy) | sorted row indices or `null` | nothing in Python |

All indices are positions into the **original** (unsorted) data.

## Selection modes

`as_selection_modes()` -> `SelectionModes(row, col, rect)`. Supported:
`"none"`, `"row"` (single), `"rows"` (multiple). `"col"`, `"cols"`, `"cell"`,
`"region"` parse but raise `RuntimeError` (not implemented). `"none"` combined
with anything raises, as does `"row"` + `"rows"` together. In the client,
clicks on a cell that is in edit mode don't toggle row selection
(`selection.tsx`).

## Narwhals rules

- Everything goes through `narwhals.stable.v1`; `as_data_frame()` uses
  `nw.from_native(eager_only=True)`, falling back (with deprecation warning)
  to `.to_pandas()` for `PandasCompatible` objects.
- **Address columns by position.** Never `data["name"]`; use
  `data.get_column(name)` for names, `data[:, i]` / `data[rows, :]` for
  positions. Resolve names once with `as_col_indexes()` (ints, incl. numpy
  ints, are always positions; `bool` raises). Pandas column names can be
  non-strings or empty.
- Duplicate column names are rejected (`test_data_frame_needs_unique_col_names`).
- On polars, positional column selection renames an empty-string column to
  `column_<i>` (see `subset_frame` docstring).

## Styles

`styles=` takes a `StyleInfo`, a list, or a function `(data) -> list[StyleInfo]`.
`as_browser_style_infos()` normalizes `rows` (int / ints / bool mask) and `cols`
(names / ints / bool mask) to index tuples; `location` must be `"body"`;
`style` must be a dict (not a CSS string); entries with neither `style` nor
`class` are dropped. Function styles run on the initial payload and again via
`updateStyles` after edits or `update_data`.

## Testing

- Playwright controller: `OutputDataFrame` in
  `shiny/playwright/controller/_output.py` (`cell_locator`, `expect_cell`,
  `expect_nrow`/`expect_ncol`, `expect_column_labels`, `select_rows`,
  `expect_selected_rows`, `set_sort`, `set_filter`, `set_cell`,
  `expect_cell_class`, `expect_class_state`, `expect_cell_title`).
- E2E apps: `tests/playwright/shiny/components/data_frame/*/` (edit,
  row_selection, styles, update_data, update_cell_value, html_columns, dtypes,
  filter_reset, ...).
- Unit: `tests/pytest/test_render_data_frame.py` (unique column names,
  selection modes, `None` data, `update_cell_value` validation),
  `tests/pytest/test_render_data_frame_tbl_data.py` (serialization, dtypes,
  patches, `subset_frame`, `as_col_indexes`, parametrized over pandas and
  polars), `tests/pytest/test_otel_data_frame.py`.
- After editing `js/data-frame/`, run `make js-build` and commit the built bundle.

## Pitfalls

- **Re-render resets all user state.** Use `update_data()` /
  `update_cell_value()` to change data without losing sort/filter.
- **`selection_mode` must be a str or tuple.** `as_selection_modes()` only
  wraps non-tuples, so a list (`["rows"]`) or set fails with
  `TypeError: unhashable type`, despite the `ListOrTuple` annotation.
- **Dead return-value check in `_patches_handler`.** It does
  `patches = tuple(val)` then tests `isinstance(patches, list)`, so the friendly
  `ValueError` loop never runs; bad shapes surface later as `KeyError` or the
  `assert`s in `_set_cell_patch_map_patches`.
- **Edited values arrive as strings.** Writing `"5"` into a numeric pandas
  column can raise (`LossySetitemError`) in `apply_frame_patches`; coerce in
  `set_patch_fn`.
- **`sort()` / `filter()` read the deprecated `_column_sort` / `_column_filter`
  inputs** and are not cached calcs; the JS sends both names, so keep both
  until the Python side moves.
- **HTML-column detection is heuristic**: only values up to index ~1000 are
  scanned, and only for `object`/`unknown` dtypes. A column whose first value is
  a plain string and later values are tags may type as `string` (see the
  "Narwhals" section of the `data_frame` docstring).
- **Unknown objects are `str()`'d** during serialization, not rejected.
- **Bounds are loose**: `update_cell_value()` does not check `row < nrow`;
  `as_cell_selection()` silently drops out-of-range rows/cols.
- **`_resolve_processed_dependencies` compares versions as strings**
  (`"10.0" < "9.0"`).
- **Legacy `<id>_selected_rows` uses JS default `.sort()`**, which is
  lexicographic (`[10, 2]`).
- **Custom messages aren't module-namespaced** by Shiny; `_send_message_to_browser`
  sends `session.ns(output_id)` so the shim finds the right element.
- Don't rename `_patches_handler` without updating `js/data-frame/` (comment in
  source).
