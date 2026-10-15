---
title: "Playwright Testing"
description: "Deep dive on py-shiny's end-to-end test infrastructure: controller class design, expect helpers, the shipped pytest fixtures and app-process runner, repo test layout, example smoke tests, Windows-specific tests, timing tests (busy-indicator progress, concurrent sessions, OTel session_start), browser/retry/tracing configuration, and flakiness pitfalls. Read before writing or changing a Playwright controller or e2e test."
---

# Playwright Testing

The overview lives in [architecture.md](architecture.md#testing-architecture)
(suites, `make` targets, tracing basics). Recipes for adding a component plus
its controller live in [componentPatterns.md](componentPatterns.md). This doc
covers how the pieces work underneath.

## Public testing API (ships in the wheel)

| Module | Contents |
| --- | --- |
| `shiny/playwright/controller/` | One controller class per UI component, exported from `controller/__init__.py` (`Chat` is re-exported from `shinychat.playwright`) |
| `shiny/playwright/expect/` | `expect_to_change`, `expect_to_have_class` / `expect_not_to_have_class`, `expect_to_have_style` / `expect_not_to_have_style`, `expect_not_to_have_attribute` |
| `shiny/playwright/_types.py` | Shared aliases: `PatternOrStr`, `ListPatternOrStr`, `AttrValue`, `StyleValue`, `Timeout` (`float \| None`) |
| `shiny/pytest/` | `create_app_fixture`, `ScopeName`; plugin module `_pytest.py` |
| `shiny/run/` | `run_shiny_app`, `ShinyAppProc` |

`shiny/playwright/__init__.py` raises a helpful `ImportError` if `playwright`
(or, when pytest is installed, `pytest-playwright`) is missing. All of this is
documented to users, so docstrings are public API docs.

## Controller architecture (`shiny/playwright/controller/`)

Design rules are written as module docstrings at the top of `_base.py`; read
them before adding a controller. Key points:

- **Base classes** in `_base.py`:
  - `UiBase`: stores `page`, `id`, `loc` (a `str` is resolved via
    `page.locator`). Exposes `.expect` == `playwright.expect(self.loc)`.
  - `UiWithContainer(UiBase)`: adds `loc_container` (default
    `"div.shiny-input-container"`). When both are strings, the container is
    narrowed to the one that *has* `loc`, and `loc` is scoped inside it; passing
    `loc="xpath=."` makes `loc` the container itself. Mixing a `str` and a
    `Locator` raises `ValueError`.
  - `UiWithLabel(UiWithContainer)`: adds `loc_label` (default
    `label#{id}-label` inside the container) and `expect_label()`.
  - `InputActionBase(UiBase)`: `expect_label`, `expect_icon`, `click` for
    action buttons/links.
  - Outputs use `_OutputBase` in `_output.py` (same `page`/`id`/`loc`/`.expect`
    shape, not a `UiBase` subclass).
- **Mixins** (suffix `M`, e.g. `WidthLocM`, `WidthContainerStyleM`,
  `_SetTextM`, `_ExpectTextInputValueM`, `_OutputInlineContainerM`) add one
  consistent method each. They are never instantiated and type `self` with a
  **Protocol** (suffix `P`: `UiBaseP`, `UiWithContainerP`, `OutputBaseP`, ...)
  describing the attributes they need. Mixins go *left* of the base class in
  the MRO, e.g. `class InputText(_SetTextM, _ExpectTextInputValueM, WidthContainerStyleM, ..., UiWithLabel)`.
  Promote a method to a mixin only when several classes share it.
- **Private bases** (`_InputSliderBase`, `_NavsetBase`, `_OverlayBase`,
  `_DateBase`, `_DownloadBase`, ...) hold shared logic per component family.
- **Constructor**: `Controller(page, id)`; the selector is built in `__init__`,
  typically tying id + tag + class, and often `.shiny-bound-input` /
  `.shiny-bound-output` (e.g. `InputText` uses
  `input#{id}[type=text].shiny-bound-input`), so locators only match once
  Shiny has bound the element.

### Method conventions

- **Locators are attributes** named `loc_*` (`loc`, `loc_container`,
  `loc_label`, `loc_title`, `loc_body`, ...), documented with an attribute
  docstring. Everything else is a method (no properties) so `timeout=` can be
  passed.
- **`expect_*()`** short names mirroring Playwright (`expect_label`, not
  `expect_label_to_have_text`). Signature shape:
  `expect_x(self, value, *, timeout: Timeout = None) -> None`. Value params
  usually accept `PatternOrStr`; `None` for an attribute/style means "must be
  absent".
- **Actions** (`set`, `click`, `open`, `close`, `toggle`, ...) only for things
  a user would do; take `*, timeout=`. `set_text()` in `_base.py` clears then
  types.
- Avoid `get_*`/value readers (the `_base.py` rule says "DO NOT provide value
  methods"); a few exist (e.g. `OutputText.get_value`) but tests should assert
  via `expect_*`.
- Never `assert` on a snapshot of DOM state; delegate to
  `playwright.expect(locator)` so the check retries.

### How `expect_*` auto-waits

Every `expect_*` bottoms out in Playwright's `LocatorAssertions`
(`to_have_text`, `to_have_attribute`, `to_have_count`, ...), which re-query
the locator until it matches or the timeout expires. `timeout=None` means
Playwright's default assertion timeout (5s); nothing in the repo overrides it
globally. Complex checks are expressed as a *single* locator so they stay
retriable:

- `expect_locator_values_in_list` / `expect_locator_contains_values_in_list`
  (`controller/_expect.py`) build one chained `xpath=.`/`has=` locator for
  checkbox/radio/select choices and assert `to_have_count(1)`; on failure they
  re-run per-item assertions purely to produce a better error.
- `expect/_internal.py` (private): `expect_attribute_to_have_value`,
  `expect_style_to_have_value`, `expect_class_to_have_value` map
  `value=None` to the `not_to_have_*` variant.
- Class/style checks in `expect/_expect.py` use word-boundary regexes against
  the `class`/`style` attribute (Playwright's `to_have_class` matches the
  whole string).
- `expect_to_change(func, timeout_secs=10)` is a context manager that polls a
  Python callable via `retry_with_timeout` (100 ms sleep, retries only on
  `AssertionError`). Use it when the state is not reachable through a locator.

`AppTestValues` (`_app_test_values.py`) is the exception to the
one-controller-per-component shape: it fetches the session's test-mode
`input`/`output`/`export` snapshot over HTTP (URL from
`window.Shiny.shinyapp.getTestSnapshotBaseUrl`), so it needs test mode and a
loaded page, else `RuntimeError`. Expected values may be predicates.

## Pytest plugin and fixtures (`shiny/pytest/`)

- Registered via `[project.entry-points.pytest11] shiny-test = "shiny.pytest._pytest"`
  in `pyproject.toml`, so the fixtures are available anywhere shiny is installed.
- `local_app` (module scope): launches `app.py` next to the test file (override
  with `@pytest.mark.parametrize("local_app", ["other.py"], indirect=True)`),
  with `SHINY_TESTMODE=1`.
- `local_server` (function scope): in-memory `shiny.testserver.test_server`
  session, no browser. Function-scoped because sessions hold input state.
- `create_app_fixture(app, scope="module", timeout_secs=30, env=None)`: the
  module-level variable name *is* the fixture name. Strings resolve relative to
  the test file; a list parametrizes the fixture. `env=None` means
  `{"SHINY_TESTMODE": "1"}`; `env` is merged over `os.environ`, so `{}` does
  not unset an inherited `SHINY_TESTMODE`.
- Repo-only helpers in `tests/playwright/conftest.py`: `create_example_fixture`
  (`examples/`), `create_doc_example_fixture`,
  `create_doc_example_core_fixture` / `create_doc_example_express_fixture`
  (`shiny/api-examples/<name>/app-core.py` / `app-express.py`).

## App processes (`shiny/run/_run.py`)

- `run_shiny_app()` spawns `python -m shiny run --port N app.py` with piped
  stdout/stderr, then `ShinyAppProc.wait_until_ready()` blocks until stderr
  shows `Uvicorn running on`. A bind error raises `ConnectionError` and the
  function retries on a new random port (`start_attempts=3`); early exit raises
  `TimeoutError` with the last 20 stderr lines.
- `ShinyAppProc` has `url` (`http://127.0.0.1:{port}/`), `port`, `proc`, and
  `stdout`/`stderr` as `OutputStream` (background reader thread; `str()` gives
  everything captured). It is a context manager; `close()` sends `terminate()`.
- Ports: `port_search_range()` gives each pytest-xdist worker
  (`PYTEST_XDIST_WORKER=gwN`) a disjoint 300-port block starting at 21000,
  wrapping after 32 workers to stay below the Linux ephemeral range.
- Internal `shiny_app_gen()` wraps the proc in `with sa:` and yields it; the
  fixtures `yield next(gen)`, so the app is terminated when the generator is
  closed/collected, and stderr is logged as a warning at teardown.

## Repo test layout

- `tests/playwright/conftest.py` is the **only** conftest. It replaces
  pytest-playwright's `page` with one session-shared page in a
  session-scoped `_session_context`: each test navigates it to `about:blank`,
  resets the viewport to 1920x1080, and moves the mouse to (0, 0). Crashed or
  "wedged" pages are replaced. Its `page.goto` wrapper retries once on
  Firefox's "interrupted by another navigation" error and on WebKit staying at
  `about:blank`. It also provides `connect_options` for a remote browser via
  `PW_TEST_CONNECT_WS_ENDPOINT` (used in CI).
- `tests/playwright/shiny/<area>/<feature>/`: `app.py` + `test_*.py`, mostly
  using `local_app` or a `create_*_fixture`. Areas include `inputs/`,
  `outputs/`, `components/`, `bookmark/`, `shiny-express/`, `bugs/`,
  `async/`, `otel/`.
- `tests/playwright/examples/`: smoke tests (below), plus `shiny create`
  template tests.
- `tests/playwright/deploys/`: apps deployed to Connect/shinyapps via
  `utils/deploy_utils.py::local_deploys_app_url_fixture`, which parametrizes
  over deploy targets *and* a `local` run; remote targets skip without
  `DEPLOY_CONNECT_SERVER_URL`/API key.
- `tests/playwright/ai_generated_apps/`: `make playwright-ai`.
- Imports like `from conftest import ...`, `from examples.example_apps import ...`,
  `from utils.deploy_utils import ...` work because `tests/playwright/` is the
  rootdir-relative import base (see the conftest header comment).

## Example smoke tests

`tests/playwright/examples/test_examples.py` and `test_api_examples.py`
parametrize over `get_apps()` (every `app.py` / `app-*.py` one level under
`examples/` or `shiny/api-examples/`) and call `validate_example()` in
`example_apps.py`, which:

1. Starts the app with `run_shiny_app`, loads it, and waits for idle via an
   injected JS port of shinytest2's `app_wait_for_idle` (or a fixed wait for
   apps in `app_hard_wait` that never settle).
2. Reloads once if both console errors and failed requests occurred (startup
   static-asset race).
3. Fails on unexpected stderr lines, JS console errors (reporting failed
   network requests), or any `.shiny-output-error` element.

Allowlists live in the same file: `app_allow_shiny_errors`,
`app_allow_external_errors`, `app_allow_js_errors`, `app_allow_output_error`.
A new example that legitimately warns needs an entry there.

## Windows-specific tests

There is no marker: Windows tests are ordinary tests under
`tests/playwright/shiny/` (they also run, and pass, in the Ubuntu jobs), and
the `playwright-windows` CI job selects them by path with
`SUB_FILE="bugs/1381-busy-indicator-progress"` on Chromium (see
[ciAndTooling.md](ciAndTooling.md#jobs-in-pytestyaml)). Add a new one by
extending that job's `SUB_FILE`/`TEST_FILE`.

## Timing tests

Some e2e tests assert *when* something happens, so they can't be pure
`expect_*` checks:

- **Busy-indicator progress** (`bugs/1381-busy-indicator-progress/`): four
  `@render.text` outputs each block the loop with `time.sleep(0.5)`.
  `page.add_init_script` wraps `window.WebSocket` to push
  `[performance.now(), data]` for every message into `window.__shinyMessages`.
  After waiting for `out4`'s value, the test clears the array, clicks
  re-render, waits again, then reads each output's first `recalculating` and
  `recalculated` times. It asserts all eight arrived (so a missing one fails
  with the collected times, not a `KeyError`) and that each gap is
  `>= MIN_GAP_MS` (250). Without the yield after `recalculating` in
  `output_obs`, Windows gaps are ~0.3 ms; macOS/Linux pass either way.
- **Concurrent sessions** (`async/concurrent_sessions/`): opens a second page
  in the same context and checks its 100 ms timer keeps ticking while the
  first tab runs a 3 s async effect. It deliberately uses
  `wait_for_timeout` + `inner_text()` because it measures elapsed ticks.
- **Streaming download** (`async/streaming_download/`): inside
  `page.expect_download()`, a value set mid-stream must reach the page and a
  click must be handled while the stream waits.
- **OTel `session_start`** (`otel/express-session-start/`): the first render
  may run before or after `session_start` ends (outputs yield before
  rendering), so the test only waits for a count matching
  `"session_start_count": [01],` and checks the closed span after a click.

## Browsers, retries, timeouts

- `make playwright` runs `$(PYTEST_BROWSERS)` = webkit, firefox, chromium
  (deploys: chromium only), with `--timeout=120 --timeout-method=thread`,
  `faulthandler_timeout=110`, and `--snapshot-warn-unused`. Root `pytest.ini`
  adds `--numprocesses auto`, `filterwarnings = error`, and the same 120 s
  thread timeout / 110 s faulthandler defaults for plain `pytest` runs (and
  takes precedence over `[tool.pytest.ini_options]` in `pyproject.toml`).
- `make playwright-debug` uses `tests/playwright/playwright-pytest.ini`:
  chromium, `--headed --slowmo=250 --maxfail=1`.
- CI (`.github/workflows/pytest.yaml`) runs one browser per matrix job,
  `--numprocesses 3` with pytest-shard (`--num-shards 4`).
- Retries are per test via pytest-rerunfailures:
  `@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)`, importing the
  constants from `examples/example_apps.py` or `utils/deploy_utils.py`
  (3 reruns, 1 when interactive). There is no global `--reruns`. For CI
  flakes on a PR, see "Handling flaky test failures in CI" in
  [commitConventions.md](commitConventions.md).
- Tracing: `PYTEST_EXTRA_ARGS="--tracing on|retain-on-failure"`, then
  `make playwright-show-trace`; implemented by `_trace_chunk` in conftest (see
  architecture.md for the video/screenshot caveats).

## Docs and controller sync

- AGENTS.md rule: every UI component needs a controller; adding or altering a
  component (new params, sub-elements, states, server-side show/hide) updates
  its controller **in the same PR**.
- New controllers must be exported in `controller/__init__.py` (`__all__`) and
  listed in `docs/_quartodoc-testing.yml` under the right section (UI Layouts,
  UI Inputs, Rendering Outputs, ...). Pytest/Run/Expect APIs are listed there
  too.
- `shiny add test` (`shiny/_main/_generate_test.py` ->
  `shiny/pytest/_generate/`) generates tests with an LLM using
  `_generate/_data/testing-documentation.json`, rebuilt from these docs by
  `make update-testing-docs`. Controller docstrings therefore feed the
  generator.

## Pitfalls

- **Shared page leaks state.** Listeners added with `page.on(...)`, cookies,
  storage, and route handlers persist across tests in the same worker; only
  URL, viewport, and mouse position are reset.
- **Hover-sensitive UI.** Firefox fires `mouseenter` on whatever loads under
  the cursor; the mouse reset handles the start of a test, but moving the
  mouse mid-test can still open tooltips/popovers.
- **Module-scoped apps.** `local_app`/`create_app_fixture` default to module
  scope: server state (reactive values, files written) carries between tests
  in a module. Reload or use `scope="function"` when tests must be independent.
- **Bound selectors.** Hand-written `page.locator("#id")` can match before
  Shiny binds; prefer controllers (which include `.shiny-bound-*`) or wait on
  an output value before acting.
- **No sleeps.** Use `expect_*`/`expect_to_change`; `page.wait_for_timeout` is
  reserved for apps that never go idle (`app_hard_wait`) and tests that
  measure elapsed time (see Timing tests).
- **Don't pass `-p no:rerunfailures`.** Tests marked `@pytest.mark.flaky`
  become unknown markers under `--strict-markers`, so their files fail to
  collect.
- **Single-shot reads.** `get_value()`, `inner_text()`, `get_attribute()` do
  not retry; asserting on them races the server.
- **Timeouts that hang.** pytest-timeout's signal method can be swallowed by
  Playwright's sync loop, hence `--timeout-method=thread` (kills the worker; the
  faulthandler dump at 110s shows where it hung).
- **Stray warnings fail tests** (`filterwarnings = error`); assert expected
  ones with `pytest.warns()`.
- **Port collisions** are handled by per-worker ranges plus bind-retry; an
  explicit `port=` bypasses the range and retries the same port.
- **Snapshots under sharding**: syrupy can't see other shards' tests, so
  regenerate stale snapshots with an unsharded all-browser
  `--snapshot-update` run.
