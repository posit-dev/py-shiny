# Design: py-shiny Test Mode (Phase A)

- **Date:** 2026-06-02
- **Issue:** rstudio/py-shiny#2269
- **Status:** Approved (brainstorming) — ready for implementation plan
- **Scope:** Phase A only. Phase B (Playwright/client integration, eval-driving JS, snapshot preprocessing) is explicitly deferred and called out where relevant.

## Goal

Port R Shiny's "test mode" to py-shiny: a faithful server-side JSON snapshot
endpoint that returns `{input, output, export}`, plus an `export_test_values()`
API for app authors to surface internal reactive values. This is the foundation
that a future Python "shinytest2-like" snapshot tool (or external automation)
can pull a full session-state dump from over HTTP.

R reference behaviors are mirrored except where explicitly noted as a deviation.

## Out of scope (deferred to Phase B)

- Client-side / Playwright access to snapshot values (a controller or `page` helper).
- Registering the built-but-unused `shiny/www/shared/shiny-testmode.js`
  (`indirectEval` helper that lets an external harness drive the app via
  `postMessage` → `eval`). This is a driving/automation concern, not part of the
  read-only snapshot endpoint.
- **Snapshot preprocessing** (`snapshotPreprocessInput` / `snapshotPreprocessOutput`
  in R): per-value author-registered transforms applied before serialization
  (used to scrub non-deterministic values like timestamps/temp paths). Core to R
  parity, but most valuable once snapshots are actually being diffed in a harness.
- R query-param surface we are **not** implementing in Phase A:
  - `format=rds` (we are JSON-only).
  - Selective `input=`/`output=`/`export=` filtering (we always return all three).
  - Per-request `sortC` sort toggle (we always sort).
- `App(..., test_mode=True)` constructor argument (env var only in Phase A; the
  constructor arg may be added later).

## 1. Enabling & flag plumbing

- **Enable mechanism:** environment variable `SHINY_TESTMODE`, truthy when
  `== "1"`. Read once at `App.__init__`.
- **Helper:** add `is_test_mode()` to `shiny/_utils.py` returning
  `os.getenv("SHINY_TESTMODE") == "1"`. Centralized so it is testable
  (monkeypatched in unit tests) and mirrors the existing
  `os.getenv("SHINY_DEV_MODE") == "1"` precedent in `html_dependencies.py:24`.
- **App:** `App.__init__` reads the helper into `self._test_mode: bool`.
  Sessions consult `self.app._test_mode`.
- **Effect when off (zero behavioral change):**
  - No output last-value recording.
  - `dataobj/shinytest` endpoint returns 404.
  - `export_test_values()` is a cheap no-op that registers nothing (so authors
    can leave the calls in production code).

## 2. `export_test_values()` API

Module-level function plus a session method (the function resolves the current
session and delegates).

```python
def export_test_values(**kwargs: Callable[[], Any]) -> None:
    """Register named values for the test-mode snapshot's `export` block.

    Uses the current reactive session. To target another session, wrap the
    call in that session's context:

        with session_context(other_session):
            export_test_values(my_val=lambda: ...)
    """
```

- **No `_session` parameter.** Always resolves via `get_current_session()`.
  Cross-session use is done by the caller with
  `with session_context(other_session):` — this exact form goes in the
  docstring/example.
- Also available as `session.export_test_values(**kwargs)`.
- Each value is a **zero-arg callable** — a plain `lambda`/function or a
  `reactive.calc` (both call with no args). Evaluated lazily at snapshot time.
- **Storage:** per-session registry `self._test_value_exports: dict[str, Callable[[], Any]]`.
- **Namespacing:** export names are namespaced with the session's `ns` prefix so
  module-exported values don't collide.
  - **DEVIATION FROM R:** R's `exportTestValues()` does NOT namespace. This must
    be marked with an explicit code comment at the registration site.
- **Off → no-op:** returns immediately without storing.
- **Duplicate names:** last-registration-wins (matches R re-running
  `exportTestValues`).

## 3. Output recording, the endpoint, and serialization

### 3a. Output last-value recording

- When test mode is on, record each output value/error as it is sent:
  - At the `set_value` call sites (`_session.py:2263`, `:2274`) write into
    `self._test_output_values: dict[str, Any]`.
  - At the `set_error` site (`:2291`) write into
    `self._test_output_errors: dict[str, Any]`.
- Accumulates across the session lifetime (last value wins). Outputs that never
  compute are simply absent — matches R, which keeps a record of the last value
  of each computed output (`private$outputValues`).
- When test mode is off, neither dict is touched.

### 3b. The endpoint

New branch in `AppSession._handle_request_impl`, alongside `upload` / `download`
/ `dynamic_route`:

```python
elif action == "dataobj" and subpath == "shinytest" and request.method == "GET":
    if not self.app._test_mode:
        return HTMLResponse("<h1>Not Found</h1>", 404)
    return await self._handle_test_snapshot(request)
```

- **404 when off** matches R's *effective* behavior: R always registers the
  data-object handler but an empty return falls through the handler chain to an
  eventual empty 404. So returning 404 here is faithful, not a deviation.
- `_handle_test_snapshot` runs inside `session_context(self)` + `reactive.isolate()`
  (the same pattern already used by the `dynamic_route` branch at
  `_session.py:1245`).
- Builds and returns:

```json
{ "input": { ... }, "output": { ... }, "export": { ... } }
```

- **`input`**: a new `Inputs._serialize_test_mode()` (see 3d).
- **`output`**: from `self._test_output_values`. An output whose most recent
  send was an error (present in `self._test_output_errors`) is represented under
  the `output` block as `{ "__shiny_output_error__": "<message>" }`. An output
  that has only ever errored has no value entry and appears solely as this error
  marker; recording an error for an id clears any prior recorded value for that
  id, and recording a value clears any prior error (mirroring
  `OutBoundMessageQueues.set_value`/`set_error` which keep values and errors
  mutually exclusive).
- **`export`**: each registered callable invoked now (lazily, inside the
  isolate); exceptions during evaluation become the tagged error marker rather
  than failing the whole snapshot.

### 3c. Serialization (best-effort, sorted)

Use **orjson**, already a dependency and already used as
`orjson.dumps(..., default=fallback)` in the data-frame renderer
(`shiny/render/_data_frame_utils/_tbl_data.py:280`) and bookmarking
(`shiny/bookmark/_utils.py`).

```python
orjson.dumps(payload, default=_snapshot_fallback, option=orjson.OPT_SORT_KEYS)
```

- `orjson` natively handles numpy / datetime / dataclasses / UUID, etc.
- `OPT_SORT_KEYS` gives stable, cleanly-diffable output (satisfies the
  determinism requirement).
- `_snapshot_fallback` stringifies values orjson cannot encode.
- A per-value `try`/`except` wraps any value that still fails serialization in a
  visible, non-fatal marker:

```json
{ "__shiny_serialization_error__": "<exception message>" }
```

  So a single bad value never hard-fails the whole snapshot, and the problem is
  visible in the output rather than silently stringified opaquely.

### 3d. Input serialization

- Add `Inputs._serialize_test_mode()` — do **not** reuse `Inputs._serialize`
  (`_session.py:1827`) directly, because it is bookmark-specific: writes file
  inputs to a `state_dir`, drops `Unserializable`, and applies bookmark
  serializers.
- `_serialize_test_mode` isolates, skips `.clientdata_*` inputs and bookmark ids,
  and runs remaining values through the 3c serialization path.
- Share the skip-list logic with `_serialize` via a small private helper to avoid
  drift.

### 3e. URL helper

- `session.get_test_snapshot_url()` →
  `session/{urllib.parse.quote(self.id)}/dataobj/shinytest?nonce={_utils.rand_hex(8)}`
  (mirrors `dynamic_route`'s URL construction at `_session.py:1426`).
- Available regardless of the flag; the endpoint only responds when test mode is
  on.

## 4. Files touched

- `shiny/session/_session.py`
  - `self._test_output_values` / `self._test_output_errors` init + recording at
    `set_value`/`set_error` sites.
  - `dataobj/shinytest` branch + `_handle_test_snapshot`.
  - `Inputs._serialize_test_mode` (+ shared skip-list helper).
  - `get_test_snapshot_url`.
  - `export_test_values` session method.
  - Abstract declarations on the `Session` ABC and `SessionProxy` delegation as
    appropriate.
- New `shiny/_export.py` (or folded into the session module) — module-level
  `export_test_values()`.
- `shiny/_app.py` — read `is_test_mode()` into `self._test_mode`.
- `shiny/_utils.py` — `is_test_mode()` helper.
- `shiny/__init__.py` (and `shiny/express/ui/__init__.py` if applicable) —
  export `export_test_values`.
- Snapshot serialization helper module/location for `_snapshot_fallback`.

## 5. Testing (pytest; Phase A is server-side, no Playwright)

- `is_test_mode()` env-var reading (monkeypatched on/off).
- `export_test_values`:
  - registers namespaced names;
  - no-op when test mode off;
  - last-registration-wins on duplicate;
  - cross-session registration via `with session_context(...)`.
- Output last-value recording:
  - accumulates last value;
  - absent until computed;
  - errors recorded into the error dict.
- End-to-end snapshot via a test `App` + Starlette `TestClient`:
  - GET the endpoint, assert `{input, output, export}` shape;
  - keys sorted;
  - serialization-error marker present for an unserializable value;
  - **404 when test mode off**.

## 6. Documentation

- Google-style docstrings for `export_test_values` (with the `session_context`
  cross-session example) and `get_test_snapshot_url`.
- Add to quartodoc YAML (`docs/_quartodoc-*.yml`, alphabetical within section).
- `CHANGELOG.md` entry referencing Issue #2269.

## Deviations from R Shiny (summary)

1. **Export names are namespaced** with the session `ns` prefix (R does not).
   Must carry an explicit code comment.
2. **JSON-only** response — no `format=rds`.
3. **No selective filtering** — `input`/`output`/`export` always all returned;
   no `input=`/`output=`/`export=` query params.
4. **Always sorted** — no per-request `sortC` toggle.
5. **Snapshot preprocessing deferred** to Phase B.
6. Enable via **`SHINY_TESTMODE` env var only** — no constructor arg in Phase A.
