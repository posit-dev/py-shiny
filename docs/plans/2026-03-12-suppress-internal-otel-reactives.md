# Design: Suppress OTel for Internal Reactive Primitives

**Date:** 2026-03-12
**Branch:** `schloerke/suppress-internal-otel`

## Problem

Shiny's OTel instrumentation emits spans and value-update logs for every
`Calc_`, `Effect_`, and `Value`. Several internal reactive primitives are
implementation details that users never interact with directly. Exposing them
in traces adds noise and can leak framework internals into telemetry.

`reactive.poll` (already fixed) demonstrated the pattern: its internal
`@reactive.effect`, `reactive.Value` objects, and timer-driven flush should
be invisible to users.

## Sites Already Suppressed

| File | Primitive | Suppressed via |
|---|---|---|
| `reactive/_poll.py` | effect + values (timer loop) | `with otel.suppress():` |
| `bookmark/_bookmark.py` | 3× effects | `@otel_suppress` |
| `session/_session.py` | output observer effect | `@otel_suppress` |
| `ui/_input_task_button.py` | task button sync effect | `@otel_suppress` |

## Remaining Sites to Suppress (this work)

### 1. `render/_data_frame.py` — `_init_reactives()`

Three `reactive.Value` objects and one `@reactive.effect` are pure
infrastructure for the DataFrame renderer:

- `self._value` — stores the rendered DataGrid/DataTable value
- `self._cell_patch_map` — stores cell edit patches
- `self._updated_data` — tracks data updates
- `@reactive.effect` calling `_attempt_update_cell_style()` — pushes cell
  style updates to the client when patches or data change

**Fix:** Wrap the entire `_init_reactives()` method body in `with otel.suppress():`.

### 2. `reactive/_extended_task.py` — `__init__`

Three `Value` objects track internal execution state:

- `self.status` — "initial" / "running" / "success" / "error" / "cancelled"
- `self.value` — task result
- `self.error` — task exception

The task execution itself already has its own dedicated OTel span
(`extended_task <fn_name>`), so these Value set/get logs are redundant noise.

**Fix:** Wrap the three `Value(...)` creations in `with otel.suppress():`.
The OTel label/level setup code above them stays outside the block.

### 3. `render/_data_frame.py` — private `@reactive_calc_method` methods

Four private (underscore-prefixed) methods are internal narwhals/view
helpers that users never call directly:

- `_nw_data` — narwhals wrapper around `data()`
- `_nw_data_patched` — narwhals wrapper around `data_patched()`
- `_data_view_all` — internal view helper (unselected rows)
- `_data_view_selected` — internal view helper (selected rows)

Five public methods (`data`, `cell_patches`, `data_patched`,
`cell_selection`, `data_view_rows`) are user-facing and remain visible.

**Fix:** Add `@otel.suppress` immediately below `@reactive_calc_method` on
each of the four private methods. The suppress level is stamped on the
function attribute and propagates through `@wraps(fn)` inside
`reactive_calc_method`'s lazy `Calc_` creation — no changes to
`reactive_calc_method` itself are needed.

## Approach

**Approach A — Targeted suppressions at each site.**

Use existing mechanisms (`with otel.suppress():` for eager primitives,
`@otel.suppress` decorator for functions passed to `@reactive_calc_method`)
consistently with existing suppressions in the codebase. No API changes.

## Tests

- DataFrame `_init_reactives`: assert the internal effect's OTel level is NONE
- DataFrame private calcs: assert `_otel_level == NONE` on each private method's
  resulting `Calc_`; assert public methods are unaffected
- ExtendedTask: assert Value set/get does not emit logs at REACTIVITY level
