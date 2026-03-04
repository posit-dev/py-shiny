# Design: `otel.collect` — counterpart to `otel.suppress`

**Date**: 2026-03-04
**Branch**: otel-followup
**Status**: Approved

## Problem

`otel.suppress` lets users disable Shiny's internal telemetry for specific reactive
objects. There is no counterpart to re-enable telemetry when the global default has
been lowered (e.g. `SHINY_OTEL_COLLECT=none`) or when a broad `otel.suppress()` block
needs a targeted exception.

## Goals

- Add `otel.collect` as a symmetric counterpart to `otel.suppress`
- Clarify that both `otel.suppress` and `otel.collect` only affect reactive object
  init-time capture, not infrastructure spans
- Keep the public API surface minimal (one new export, one private helper)

## Design

### API Shape

`otel.collect` follows the exact same dual-use pattern as `otel.suppress`:

```python
# Decorator (no parens)
@reactive.calc
@otel.collect
def my_calc(): ...

# Context manager (parens required)
with otel.collect():
    @reactive.calc
    def my_calc(): ...
```

### Behavior

| API | Effect on reactive init-time capture | Effect on infrastructure spans |
|-----|--------------------------------------|-------------------------------|
| `otel.suppress` | Forces to `NONE` | None — always reads env var |
| `otel.collect` | Forces to `ALL` | None — always reads env var |

"Infrastructure spans" are those with no corresponding reactive object:
`session.start`, `session.end`, `reactive_update`, `restore_bookmark_callbacks`.

### Contextvar Semantics

`otel.collect()` sets the contextvar to `ALL` on enter and resets it to its previous
value on exit via `ContextVar.reset(token)`. Nesting works correctly:

```python
with otel.suppress():       # contextvar → NONE
    with otel.collect():    # contextvar → ALL
        @reactive.calc
        def my_calc(): ...  # captures ALL
                            # contextvar → NONE (restored)
    @reactive.calc
    def other_calc(): ...   # captures NONE
                            # contextvar → None (env var resolution restored)
```

### Infrastructure Span Isolation

A new private `_get_env_level()` helper in `_collect.py` reads only the env var,
bypassing the contextvar entirely. Infrastructure span callers in `_session.py`,
`_core.py`, and `_bookmark.py` switch from `get_level()` to `_get_env_level()`.

`otel.get_level()` remains the single public level-inspection function. It continues
to read contextvar → env var fallback, correctly reflecting suppress/collect state.

### Documentation Phrasing

One-liners avoid repeating the API name and don't expose enum values:

- `otel.suppress` — "Disables Shiny's internal telemetry"
- `otel.collect` — "Enables Shiny's internal telemetry"

## Implementation Scope

All changes are in `shiny/otel/` and the three infrastructure callers:

1. **`_collect.py`**: Add private `_get_env_level()` (env var only, no contextvar)
2. **`_decorators.py`**: Add `_CollectContext`, `_Collect`, and `collect` singleton
3. **`__init__.py`**: Export `collect` alongside `suppress`; update docstring
4. **`_session.py`**, **`_core.py`**, **`_bookmark.py`**: Replace `get_level()` calls
   in infrastructure spans with `_get_env_level()`
5. **`examples/open-telemetry/`**, **`docs/`**: Update examples and docstrings

No changes needed to `_function_attrs.py`, `_span_wrappers.py`, or any reactive code.
