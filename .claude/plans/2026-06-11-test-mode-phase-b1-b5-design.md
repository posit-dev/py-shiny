# Design: Test Mode Phase B1 + B5

- **Date:** 2026-06-11
- **Issue:** rstudio/py-shiny#2269 (Phase B follow-up to Phase A)
- **Status:** Approved (brainstorming) — ready for implementation plan
- **Scope:** This cycle = **B1** (Playwright access to the test snapshot) + **B5** (`App(test_mode=)` constructor argument). Deferred to later, separate specs: **B2** (snapshot preprocessing), then **B4** (endpoint query-param surface), then **B3** (`shiny-testmode.js` eval-driving asset — especially if R's shinytest2 utilizes it).

## Background

Phase A added a server-side test snapshot: when test mode is on (`SHINY_TESTMODE=1`),
each session records the last value/error of every output, app authors can register
values with `export_test_values()`, and `GET /session/{id}/dataobj/shinytest` returns
`{"input": {...}, "output": {...}, "export": {...}}` as sorted JSON (404 when off).
`session.get_test_snapshot_url()` builds that path server-side.

Phase B1 makes that snapshot consumable from py-shiny's primary e2e testing story
(Playwright controllers). Phase B5 adds a constructor argument to enable test mode
programmatically (needed so test apps can opt in without relying solely on the env var).

Key prior finding: the **vendored client JS already exposes**
`window.Shiny.shinyapp.getTestSnapshotBaseUrl({fullUrl: true})`, which returns the full
URL `…/session/<sessionId>/dataobj/shinytest?w=<workerId>&nonce=<random>`. This is the
same mechanism R's shinytest2 uses. Our Phase A endpoint ignores the `w`/`nonce` query
params, so it is compatible.

## Out of scope (deferred)

- **B2** snapshot preprocessing (`snapshot_preprocess_input` / `snapshot_preprocess_output`).
- **B4** endpoint query params (`format=rds`, selective `input=/output=/export=`, `sortC`).
- **B3** registering `shiny-testmode.js` (eval-driving asset).
- Whole-block `expect_inputs/outputs/exports` are **not implemented** this cycle — see §2.

## 1. `App(test_mode=)` + fixture wiring (B5 + Option A)

### 1a. Constructor argument

- Add keyword-only `test_mode: bool | None = None` to `App.__init__` (alongside `debug`).
- Resolution (replaces the current unconditional `is_test_mode()` read):

```python
self._test_mode: bool = is_test_mode() if test_mode is None else test_mode
```

- Explicit `True`/`False` wins; `None` (default) falls back to the `SHINY_TESTMODE`
  env var. Backward-compatible with Phase A.

### 1b. Fixture wiring — Option A (global for e2e apps)

All Playwright-launched apps run in test mode, scoped to the launched subprocess (not
the pytest process's own `os.environ`, and not affecting general callers of the
launcher).

- Thread an `env: dict[str, str] | None = None` parameter through the app-launch path:
  - `run_shiny_app()` (`shiny/run/_run.py`) merges it into the subprocess environment:
    `Popen(..., env={**os.environ, **(env or {})})`.
  - `shiny_app_gen()` / `create_app_fixture()` (`shiny/pytest/_fixture.py`) forward `env`.
- The pytest app-launch fixtures pass `env={"SHINY_TESTMODE": "1"}` by default, so every
  fixture-launched app is in test mode.
- `run_shiny_app`'s general (non-test) callers are unaffected (default `env=None` → no
  test-mode injection).

## 2. The `AppTestValues` controller (B1)

### 2a. Location & export

- New file: `shiny/playwright/controller/_app_test_values.py`.
- Export `AppTestValues` from `shiny/playwright/controller/__init__.py` (and confirm any
  `shiny.playwright` re-export path used by the other controllers).

### 2b. Construction & URL discovery

- `AppTestValues(page)` — session-global; takes only `page` (no `id`/`loc`). It uses a
  lightweight base (not `UiWithContainer`/`UiWithLabel`, which assume a DOM element).
- Discovers the snapshot URL via the client's own method:

```python
url = page.evaluate("() => window.Shiny.shinyapp.getTestSnapshotBaseUrl({fullUrl: true})")
```

  A fresh call per fetch yields a new `nonce` (cache-bust).

### 2c. Fetch

- `page.request.get(url)` (Playwright `APIRequestContext`, shares the browser context) →
  `response.json()`.

### 2d. Method surface

Implemented this cycle:

```python
av = AppTestValues(page)

# Per-key expectations — auto-retry (re-fetch) until match or timeout.
av.expect_input("n", 20)
av.expect_output("txt", "n = 20")
av.expect_export("doubled", 40)

# Escape hatch — single fetch, no retry.
data = av.get()   # raw {"input": {...}, "output": {...}, "export": {...}}
```

- Matching is against the **JSON-decoded** value (pass Python `20`, `"n = 20"`,
  `{"a": 1}`).
- Keys are the raw server-side snapshot keys (namespaced ids such as `"mod1-foo"`, exactly
  as they appear in the snapshot).

**Commented placeholders + TODO only** (NOT implemented this cycle):

```python
# TODO(phase-b): expect_inputs / expect_outputs / expect_exports
#   Compare a provided dict against the corresponding snapshot block, treating the
#   given dict as a subset (or full) set of keys to match. Decide/encode the
#   comparison mode (subset vs full) when implementing.
# def expect_inputs(self, values: dict[str, Any], *, timeout: float | None = None) -> None: ...
# def expect_outputs(self, values: dict[str, Any], *, timeout: float | None = None) -> None: ...
# def expect_exports(self, values: dict[str, Any], *, timeout: float | None = None) -> None: ...
```

### 2e. Auto-retry

- `expect_*` methods re-fetch the snapshot inside a retry loop (reuse the existing
  `retry_with_timeout` pattern from `shiny/playwright/expect/`) until the assertion holds
  or the default timeout elapses — handling async output/export settling.
- `get()` performs a single fetch (no retry).

### 2f. Error behavior

- If used against an app **not** in test mode, `getTestSnapshotBaseUrl` still returns a
  URL but the endpoint returns 404. The helper detects a non-OK response (or a
  non-JSON/HTML body) and raises a clear error, e.g.:
  `"Test-mode snapshot endpoint returned <status>; enable test mode via App(test_mode=True) or SHINY_TESTMODE=1."`
  — rather than surfacing a raw JSON-decode failure.

## 3. Test apps & tests

### 3a. Playwright test app

- New folder `tests/playwright/shiny/test_mode/` with an `app.py` that:
  - constructs `App(app_ui, server, test_mode=True)` (exercises B5 directly and is
    self-documenting; a brief comment notes this is intentional even though the fixture
    also enables test mode globally);
  - has an input (e.g. `ui.input_slider("n", ...)`), an output depending on it, and an
    `export_test_values(...)` of an internal `reactive.calc`.

### 3b. E2E test (`test_app_test_values.py`)

- Drive the input via existing controllers (e.g. `InputSlider`), then use
  `AppTestValues(page)` to:
  - `expect_input("n", <value>)`, `expect_output(...)`, `expect_export(...)` after the
    interaction (verifies auto-retry across async settle);
  - `get()` and assert the `{input, output, export}` shape;
  - (optional, if easy) assert an errored output surfaces the `__shiny_output_error__`
    marker.

### 3c. Unit tests (`tests/pytest/`)

- **B5** (extend `test_test_mode.py`):
  - `App(test_mode=True)._test_mode is True`;
  - `App(test_mode=False)._test_mode is False` even when `SHINY_TESTMODE=1` is set;
  - `App()` (None) follows the env var (both on and off).
- **Fixture env plumbing:** assert `run_shiny_app(..., env=...)` (and the
  `create_app_fixture`/`shiny_app_gen` forwarding) threads env into the subprocess. If
  exercising a real subprocess is awkward to unit-test, assert the parameter is forwarded
  (e.g. via monkeypatching `Popen`) and rely on the e2e run for end-to-end coverage.

## 4. Docs, controller registration & changelog

- **Export & docs:** export `AppTestValues` from
  `shiny/playwright/controller/__init__.py`; add it to `docs/_quartodoc-testing.yml`
  (alphabetical).
- **Controller documentation test:** `tests/pytest/test_controller_documentation.py`
  asserts every controller is documented — the new controller and its public methods must
  satisfy it (Google-style docstrings on the class and each public `expect_*` / `get`
  method; include an `Examples` section if the renderer/test requires one).
- **Docstrings:** class docstring states the test-mode requirement and shows a short usage
  example; each `expect_*` documents key/value matching and auto-retry/timeout.
- **CHANGELOG.md:** under `[UNRELEASED]` → New features, add the `AppTestValues` Playwright
  controller and the `App(test_mode=)` argument (#2269).

## Deviations / notes

- URL discovery relies on the vendored client method `getTestSnapshotBaseUrl` (R-shinytest
  compatible); we do not reconstruct the URL from internal client config paths.
- Whole-block `expect_*s` are placeholders only this cycle (subset/full key comparison TBD
  at implementation time).
- Option A (global test mode for e2e apps) is acceptable today because Phase A test mode is
  behavior-neutral for the UI (recording is additive — two dict writes per output send).
  When B3 (eval-driving JS) lands, revisit whether it should activate globally under test
  mode.
