# Test Mode Phase B1 + B5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Phase A test-mode snapshot consumable from Playwright e2e tests via a new `AppTestValues(page)` controller, and add an `App(test_mode=)` constructor argument; wire the pytest app-launch fixtures to run apps in test mode.

**Architecture:** `App(test_mode: bool | None = None)` resolves to the explicit value or the `SHINY_TESTMODE` env var. The app-launch path (`run_shiny_app`/`shiny_app_gen`) gains an `env` parameter that the pytest fixtures use to inject `SHINY_TESTMODE=1` into the launched subprocess. The `AppTestValues` controller discovers the snapshot URL from the vendored client method `window.Shiny.shinyapp.getTestSnapshotBaseUrl({fullUrl: true})`, fetches it with `page.request.get(...)`, and exposes auto-retrying `expect_input/output/export(key, value)` plus a raw `get()`.

**Tech Stack:** Python, Playwright (sync API), Starlette, orjson (server side), pytest + pytest-asyncio.

**Spec:** `.claude/plans/2026-06-11-test-mode-phase-b1-b5-design.md` (Issue rstudio/py-shiny#2269).

## Conventions for the implementer

- **Run pytest in this sandbox** with the project venv and the rerunfailures plugin disabled (it binds a socket the sandbox blocks):
  `.venv/bin/python -m pytest <paths> -q -p no:rerunfailures`
- **Do NOT** add `Co-Authored-By: Claude ...` trailers to commits. Use the exact commit messages given.
- Commit to the **current branch** (`git branch --show-current`); do not switch branches.
- Imports at the top of files.

## File Structure

- `shiny/_app.py` — add `test_mode` constructor param (B5).
- `shiny/run/_run.py` — add `env` param + `_subprocess_env` helper; thread through `run_shiny_app` and `shiny_app_gen`.
- `shiny/pytest/_pytest.py` (`local_app`), `shiny/pytest/_fixture.py` (`create_app_fixture`) — pass `env` defaulting to test mode.
- `shiny/playwright/controller/_app_test_values.py` — NEW: `AppTestValues` controller.
- `shiny/playwright/controller/__init__.py` — export `AppTestValues`.
- `docs/_quartodoc-testing.yml` — document `AppTestValues`.
- `tests/playwright/shiny/test_mode/app.py`, `tests/playwright/shiny/test_mode/test_app_test_values.py` — NEW e2e app + test.
- `tests/pytest/test_test_mode.py` — extend with B5 + env-threading unit tests.
- `CHANGELOG.md` — entry.

---

## Task 1: `App(test_mode=)` constructor argument (B5)

**Files:**
- Modify: `shiny/_app.py` (class docstring Parameters ~line 87; `__init__` signature ~line 161; `_test_mode` assignment ~line 183)
- Test: `tests/pytest/test_test_mode.py`

- [ ] **Step 1: Write the failing tests**

Append to the END of `tests/pytest/test_test_mode.py`:

```python
def test_app_test_mode_arg_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Explicit True wins even when the env var is unset.
    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    assert App(ui.TagList(), None, test_mode=True)._test_mode is True

    # Explicit False wins even when the env var says on.
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    assert App(ui.TagList(), None, test_mode=False)._test_mode is False


def test_app_test_mode_none_follows_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    assert App(ui.TagList(), None, test_mode=None)._test_mode is True

    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    assert App(ui.TagList(), None)._test_mode is False  # default is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/pytest/test_test_mode.py -k "test_app_test_mode" -v -p no:rerunfailures`
Expected: FAIL with `TypeError: __init__() got an unexpected keyword argument 'test_mode'`.

- [ ] **Step 3: Add the constructor parameter**

In `shiny/_app.py`, add the parameter to `App.__init__` immediately after `debug: bool = False,` (line 161):

```python
        debug: bool = False,
        test_mode: bool | None = None,
```

Then change the `_test_mode` assignment (currently line 183, `self._test_mode: bool = is_test_mode()`) to:

```python
        self._test_mode: bool = is_test_mode() if test_mode is None else test_mode
        """Whether Shiny test mode is enabled.

        Defaults to the ``SHINY_TESTMODE`` env var when ``test_mode`` is ``None``.
        """
```

Finally, document the parameter in the class docstring's `Parameters` section, immediately after the `debug` entry (after line 88, `Whether to enable debug mode.`):

```python
    test_mode
        Whether to enable Shiny test mode. When ``None`` (the default), this follows
        the ``SHINY_TESTMODE`` environment variable. When test mode is enabled, the
        session records output values and serves a JSON snapshot at
        ``/session/{id}/dataobj/shinytest``.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/pytest/test_test_mode.py -k "test_app_test_mode" -v -p no:rerunfailures`
Expected: PASS (2 tests). Also run the whole file: `.venv/bin/python -m pytest tests/pytest/test_test_mode.py -q -p no:rerunfailures` — all PASS.

- [ ] **Step 5: Commit**

```bash
git add shiny/_app.py tests/pytest/test_test_mode.py
git commit -m "feat: Add App(test_mode=) constructor argument (#2269)"
```

---

## Task 2: Thread `env` through the app-launch path

**Files:**
- Modify: `shiny/run/_run.py` (add `_subprocess_env` helper; `run_shiny_app` ~lines 205-292; `shiny_app_gen` ~lines 297-349)
- Test: `tests/pytest/test_run_env.py` (create)

- [ ] **Step 1: Write the failing tests**

Create `tests/pytest/test_run_env.py`:

```python
"""Tests for env-var injection in the app-launch path."""

from __future__ import annotations

import os
from unittest import mock

import pytest

from shiny.run import _run


def test_subprocess_env_none_returns_none() -> None:
    assert _run._subprocess_env(None) is None


def test_subprocess_env_merges_with_os_environ(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EXISTING_VAR", "keep")
    merged = _run._subprocess_env({"SHINY_TESTMODE": "1"})
    assert merged is not None
    assert merged["SHINY_TESTMODE"] == "1"
    assert merged["EXISTING_VAR"] == "keep"  # inherits parent env


def test_run_shiny_app_passes_env_to_popen() -> None:
    captured: dict[str, object] = {}

    class _FakeProc:
        stdout = None
        stderr = None

        def wait(self) -> int:
            return 0

    def fake_popen(*args: object, **kwargs: object):
        captured.update(kwargs)
        return _FakeProc()

    with mock.patch.object(_run.subprocess, "Popen", fake_popen):
        with mock.patch.object(_run, "ShinyAppProc") as fake_app_proc:
            _run.run_shiny_app(
                "app.py", wait_for_start=False, env={"SHINY_TESTMODE": "1"}
            )

    assert fake_app_proc.called
    assert "env" in captured
    env_arg = captured["env"]
    assert isinstance(env_arg, dict)
    assert env_arg["SHINY_TESTMODE"] == "1"
    assert env_arg.get("PATH") == os.environ.get("PATH")  # merged with parent env
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/pytest/test_run_env.py -v -p no:rerunfailures`
Expected: FAIL — `AttributeError: module 'shiny.run._run' has no attribute '_subprocess_env'` and `run_shiny_app() got an unexpected keyword argument 'env'`.

- [ ] **Step 3: Add the helper and thread `env`**

In `shiny/run/_run.py`, add this module-level helper just above `def run_shiny_app(` (line 205):

```python
def _subprocess_env(env: dict[str, str] | None) -> dict[str, str] | None:
    """
    Build the environment for a launched app subprocess.

    Returns ``None`` (inherit the parent environment unchanged) when ``env`` is
    ``None``; otherwise returns the parent environment merged with ``env``.
    """
    if env is None:
        return None
    return {**os.environ, **env}
```

Confirm `import os` is present at the top of `shiny/run/_run.py` (add it to the stdlib imports if missing).

Add an `env` parameter to `run_shiny_app` (after `bufsize: int = 64 * 1024,` at line 213):

```python
    bufsize: int = 64 * 1024,
    env: dict[str, str] | None = None,
```

Use it in the `Popen` call by adding the `env` keyword (after `cwd=cwd,` at line 259):

```python
        cwd=cwd,
        env=_subprocess_env(env),
        encoding="utf-8",
```

Forward `env` in the recursive retry call (inside `run_shiny_app`, the `return run_shiny_app(...)` block ~lines 282-290) by adding `env=env,` to that call:

```python
            return run_shiny_app(
                app_file,
                start_attempts=start_attempts,
                port=port,
                cwd=cwd,
                wait_for_start=wait_for_start,
                timeout_secs=timeout_secs,
                bufsize=bufsize,
                env=env,
            )
```

Add an `env` parameter to `shiny_app_gen` (after `bufsize: int = 64 * 1024,` at line 305):

```python
    bufsize: int = 64 * 1024,
    env: dict[str, str] | None = None,
```

Forward it in the `run_shiny_app(...)` call inside `shiny_app_gen` (~lines 341-349) by adding `env=env,`:

```python
    sa = run_shiny_app(
        app_file,
        wait_for_start=True,
        start_attempts=start_attempts,
        port=port,
        cwd=cwd,
        bufsize=bufsize,
        timeout_secs=timeout_secs,
        env=env,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/pytest/test_run_env.py -v -p no:rerunfailures`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add shiny/run/_run.py tests/pytest/test_run_env.py
git commit -m "feat: Thread env into the Shiny app-launch subprocess path (#2269)"
```

---

## Task 3: Fixtures launch apps in test mode

**Files:**
- Modify: `shiny/pytest/_pytest.py` (`local_app`, ~line 22)
- Modify: `shiny/pytest/_fixture.py` (`create_app_fixture`, add `env` param + forward; ~lines 36-151)
- Test: `tests/pytest/test_run_env.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/pytest/test_run_env.py`:

```python
def test_create_app_fixture_accepts_env_param() -> None:
    """create_app_fixture exposes an `env` override and returns a fixture."""
    import inspect

    from shiny.pytest import create_app_fixture

    sig = inspect.signature(create_app_fixture)
    assert "env" in sig.parameters

    # Returns a callable (a pytest fixture function) without launching anything.
    fixture = create_app_fixture("app.py")
    assert callable(fixture)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/pytest/test_run_env.py -k create_app_fixture -v -p no:rerunfailures`
Expected: FAIL — `assert "env" in sig.parameters` fails (param not present).

- [ ] **Step 3: Default the fixtures to test mode**

In `shiny/pytest/_pytest.py`, change the `local_app` fixture body (line 22) from:

```python
    sa_gen = shiny_app_gen(PurePath(request.path).parent / app_file)
```

to:

```python
    sa_gen = shiny_app_gen(
        PurePath(request.path).parent / app_file,
        env={"SHINY_TESTMODE": "1"},
    )
```

In `shiny/pytest/_fixture.py`:

(a) Add an `env` parameter to `create_app_fixture` (after `timeout_secs: float = 30,` at line 39):

```python
    timeout_secs: float = 30,
    env: dict[str, str] | None = None,
```

(b) Just inside the function body (before `def get_app_path(...)` at line 127), resolve the default:

```python
    # Launched apps run in Shiny test mode by default so the `AppTestValues`
    # controller works out of the box. Pass `env={}` (or custom env) to opt out.
    effective_env = {"SHINY_TESTMODE": "1"} if env is None else env
```

(c) Forward `effective_env` in BOTH `shiny_app_gen(...)` calls (the list branch ~line 139 and the single branch ~line 148):

```python
            sa_gen = shiny_app_gen(
                app_path, timeout_secs=timeout_secs, env=effective_env
            )
```
(apply the identical change to both `shiny_app_gen(...)` call sites).

(d) Document the new parameter in the `create_app_fixture` docstring `Parameters` section, after the `timeout_secs` entry (after line 75):

```python
    env
        Extra environment variables for the launched app subprocess, merged over the
        parent environment. When ``None`` (the default), ``{"SHINY_TESTMODE": "1"}``
        is used so the app runs in Shiny test mode (enabling the `AppTestValues`
        controller). Pass an explicit dict (e.g. ``{}``) to override.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/pytest/test_run_env.py -k create_app_fixture -v -p no:rerunfailures`
Expected: PASS.

Note: behavioral proof that the env actually reaches the launched app (and thus enables test mode) is the e2e test in Task 5.

- [ ] **Step 5: Commit**

```bash
git add shiny/pytest/_pytest.py shiny/pytest/_fixture.py tests/pytest/test_run_env.py
git commit -m "feat: Launch Playwright fixture apps in test mode by default (#2269)"
```

---

## Task 4: `AppTestValues` controller + registration

**Files:**
- Create: `shiny/playwright/controller/_app_test_values.py`
- Modify: `shiny/playwright/controller/__init__.py` (imports + `__all__`)
- Modify: `docs/_quartodoc-testing.yml`
- Test: `tests/pytest/test_controller_documentation.py` (existing; drives red→green)

- [ ] **Step 1: Create the controller and export it (this makes the documentation test fail first)**

Create `shiny/playwright/controller/_app_test_values.py`:

```python
from __future__ import annotations

from typing import Any

from playwright.sync_api import Page

from ..expect._expect_to_change import retry_with_timeout

__all__ = ("AppTestValues",)

_DEFAULT_TIMEOUT_SECS = 30


class AppTestValues:
    """
    Read a Shiny session's test-mode snapshot of `input`, `output`, and `export`
    values from a running app.

    Requires the app to be running in test mode (construct the app with
    `App(test_mode=True)` or set the `SHINY_TESTMODE=1` environment variable);
    otherwise the snapshot endpoint is not served and the methods raise a
    `RuntimeError`. The pytest app-launch fixtures (`local_app`,
    `create_app_fixture`) enable test mode by default.

    The snapshot URL is discovered from the Shiny client itself
    (`window.Shiny.shinyapp.getTestSnapshotBaseUrl(...)`) and fetched over HTTP, so
    the app must be loaded in the page before these methods are called.

    Examples
    --------
    ```python
    from shiny.playwright import controller

    app_values = controller.AppTestValues(page)
    app_values.expect_input("name", "abc")
    app_values.expect_output("greeting", "Hello abc")
    app_values.expect_export("upper", "ABC")
    snapshot = app_values.get()  # {"input": {...}, "output": {...}, "export": {...}}
    ```
    """

    page: Page
    """Playwright `Page` of the Shiny app."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def _fetch(self) -> dict[str, Any]:
        url = str(
            self.page.evaluate(
                "() => window.Shiny.shinyapp.getTestSnapshotBaseUrl({fullUrl: true})"
            )
        )
        response = self.page.request.get(url)
        if not response.ok:
            raise RuntimeError(
                f"Test-mode snapshot request to {url} returned HTTP "
                f"{response.status}. Enable test mode via `App(test_mode=True)` or "
                f"the `SHINY_TESTMODE=1` environment variable."
            )
        return response.json()

    def get(self) -> dict[str, Any]:
        """
        Return the raw test-mode snapshot.

        Returns
        -------
        :
            A dict with `"input"`, `"output"`, and `"export"` keys, each mapping
            (namespaced) ids to their JSON-decoded values. Performs a single fetch
            (no retry).
        """
        return self._fetch()

    def _expect_value(
        self, block: str, key: str, value: Any, timeout: float | None
    ) -> None:
        @retry_with_timeout(timeout if timeout is not None else _DEFAULT_TIMEOUT_SECS)
        def _() -> None:
            section = self._fetch()[block]
            if key not in section:
                raise AssertionError(
                    f"{block}[{key!r}] is not present in the test snapshot. "
                    f"Present keys: {sorted(section)}"
                )
            actual = section[key]
            if actual != value:
                raise AssertionError(
                    f"{block}[{key!r}] == {actual!r}, expected {value!r}"
                )

        _()

    def expect_input(
        self, key: str, value: Any, *, timeout: float | None = None
    ) -> None:
        """
        Expect the input `key` to equal `value` (JSON-decoded), retrying until it
        matches or `timeout` seconds elapse.
        """
        self._expect_value("input", key, value, timeout)

    def expect_output(
        self, key: str, value: Any, *, timeout: float | None = None
    ) -> None:
        """
        Expect the output `key` to equal `value` (JSON-decoded), retrying until it
        matches or `timeout` seconds elapse.
        """
        self._expect_value("output", key, value, timeout)

    def expect_export(
        self, key: str, value: Any, *, timeout: float | None = None
    ) -> None:
        """
        Expect the exported value `key` to equal `value` (JSON-decoded), retrying
        until it matches or `timeout` seconds elapse.
        """
        self._expect_value("export", key, value, timeout)

    # TODO(phase-b): whole-block expectations.
    #   Compare a provided dict against the corresponding snapshot block, treating
    #   the given dict as a subset (or full) set of keys to match. Decide/encode the
    #   comparison mode (subset vs full) when implementing.
    # def expect_inputs(self, values: dict[str, Any], *, timeout: float | None = None) -> None: ...
    # def expect_outputs(self, values: dict[str, Any], *, timeout: float | None = None) -> None: ...
    # def expect_exports(self, values: dict[str, Any], *, timeout: float | None = None) -> None: ...
```

In `shiny/playwright/controller/__init__.py`, add the import. Place it after the `from ._accordion import (...)` block (line 3-6) so it reads naturally near the top of the import group:

```python
from ._app_test_values import AppTestValues
```

And add `"AppTestValues"` to the `__all__` list (it begins at line 76). Add it as the first entry for visibility:

```python
__all__ = [
    "AppTestValues",
    "InputActionButton",
```

- [ ] **Step 2: Run the documentation test to verify it now fails**

Run: `.venv/bin/python -m pytest tests/pytest/test_controller_documentation.py -v -p no:rerunfailures`
Expected: FAIL — `Controllers missing from .../docs/_quartodoc-testing.yml: - playwright.controller.AppTestValues` (the new public class is exported but not documented).

- [ ] **Step 3: Document the controller**

In `docs/_quartodoc-testing.yml`, add a new section. Insert it immediately after the `- title: Rendering Outputs` section (which ends at line 89 with `- playwright.controller.OutputUi`) and before `- title: "Playwright Expect"` (line 90). Match the existing 4-space/6-space indentation exactly:

```yaml
    - title: App test values
      desc: Read a session's test-mode snapshot of input, output, and export values.
      contents:
        - playwright.controller.AppTestValues
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/pytest/test_controller_documentation.py -v -p no:rerunfailures`
Expected: PASS.

Also confirm the import resolves and the class is reachable:
`.venv/bin/python -c "from shiny.playwright import controller; print(controller.AppTestValues)"`
Expected: prints the class.

- [ ] **Step 5: Commit**

```bash
git add shiny/playwright/controller/_app_test_values.py shiny/playwright/controller/__init__.py docs/_quartodoc-testing.yml
git commit -m "feat: Add AppTestValues Playwright controller (#2269)"
```

---

## Task 5: End-to-end test app + Playwright test

**Files:**
- Create: `tests/playwright/shiny/test_mode/app.py`
- Create: `tests/playwright/shiny/test_mode/test_app_test_values.py`

- [ ] **Step 1: Write the test app**

Create `tests/playwright/shiny/test_mode/app.py`:

```python
from shiny import App, Inputs, Outputs, Session, export_test_values, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_text("name", "Name", value="abc"),
    ui.input_slider("n", "N", min=0, max=100, value=20),
    ui.output_text_verbatim("double_txt"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def doubled() -> int:
        return int(input.n()) * 2

    @render.text
    def double_txt() -> str:
        return f"doubled = {doubled()}"

    # Surface an internal reactive value in the test-mode snapshot.
    export_test_values(doubled=doubled)


# `test_mode=True` is intentional: it exercises the `App(test_mode=)` constructor
# path even though the test fixtures also enable test mode globally.
app = App(app_ui, server, test_mode=True)
```

- [ ] **Step 2: Write the Playwright test**

Create `tests/playwright/shiny/test_mode/test_app_test_values.py`:

```python
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_app_test_values(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Ensure the app is loaded/bound before reading the snapshot.
    controller.InputText(page, "name").expect_value("abc")

    app_values = controller.AppTestValues(page)

    # Per-key expectations (auto-retry across async settle).
    app_values.expect_input("name", "abc")
    app_values.expect_output("double_txt", "doubled = 40")
    app_values.expect_export("doubled", 40)

    # Raw snapshot shape.
    data = app_values.get()
    assert set(data.keys()) == {"input", "output", "export"}
    assert data["export"]["doubled"] == 40

    # Change inputs; the snapshot reflects the new values (auto-retry).
    controller.InputText(page, "name").set("xyz")
    app_values.expect_input("name", "xyz")

    controller.InputSlider(page, "n").set("30")
    app_values.expect_output("double_txt", "doubled = 60")
    app_values.expect_export("doubled", 60)
```

- [ ] **Step 3: Run the e2e test**

Run (requires Playwright browsers installed; if they are not available in this environment, this is the one task whose behavioral verification happens in CI):

`.venv/bin/python -m pytest tests/playwright/shiny/test_mode/test_app_test_values.py --browser chromium -p no:rerunfailures -v`

Expected: PASS. If browsers are not installed locally, run `.venv/bin/python -m playwright install chromium` first; if that is not possible in the sandbox, report DONE_WITH_CONCERNS noting the test could not be executed locally and must be verified in CI. Do NOT mark the behavior verified if it did not run.

- [ ] **Step 4: Commit**

```bash
git add tests/playwright/shiny/test_mode/app.py tests/playwright/shiny/test_mode/test_app_test_values.py
git commit -m "test: Add e2e test for AppTestValues controller (#2269)"
```

---

## Task 6: Type check, format, and CHANGELOG

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Generate typings and run pyright on the changed files**

Generate the stubs CI uses (no network beyond a public git clone; needed for a clean pyright run):
`export PATH="$PWD/.venv/bin:$PATH" && make pyright-typings`

Then run pyright over the whole project (as CI does):
`export PATH="$PWD/.venv/bin:$PATH" && pyright`
Expected: `0 errors`. If a NEW error appears in one of the feature files (`shiny/_app.py`, `shiny/run/_run.py`, `shiny/pytest/_fixture.py`, `shiny/pytest/_pytest.py`, `shiny/playwright/controller/_app_test_values.py`, the new tests), fix it minimally. Likely spot: `self.page.evaluate(...)` returns `Any` (already wrapped in `str(...)`); `response.json()` returns `Any` (fine to return as `dict[str, Any]`).

- [ ] **Step 2: Format and lint the changed files**

```bash
export PATH="$PWD/.venv/bin:$PATH"
black shiny/ tests/ docs/
isort shiny/ tests/
flake8 shiny/playwright/controller/_app_test_values.py shiny/run/_run.py shiny/pytest/_fixture.py shiny/pytest/_pytest.py shiny/_app.py tests/pytest/test_run_env.py tests/playwright/shiny/test_mode/
```
Expected: black reports files unchanged (or reformats; re-stage if so); isort clean; flake8 exits 0.

- [ ] **Step 3: Add the CHANGELOG entry**

In `CHANGELOG.md`, under the existing `## [UNRELEASED]` → `### New features` section, add:

```markdown
* Added the `AppTestValues` Playwright controller for reading a session's test-mode snapshot (`input`/`output`/`export`) in end-to-end tests, plus an `App(test_mode=)` constructor argument (defaulting to the `SHINY_TESTMODE` env var). The pytest app-launch fixtures (`local_app`, `create_app_fixture`) now run apps in test mode by default. (#2269)
```

- [ ] **Step 4: Verify the unit suite is green**

Run: `.venv/bin/python -m pytest tests/pytest/test_test_mode.py tests/pytest/test_run_env.py tests/pytest/test_controller_documentation.py -q -p no:rerunfailures`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: Document AppTestValues and App(test_mode=) (#2269)"
```

---

## Self-Review Notes (for the implementer)

- **Spec coverage:** B5 constructor arg (Task 1); env threading (Task 2); fixtures default to test mode (Task 3); `AppTestValues` controller with `get()` + per-key `expect_*`, URL discovery via `getTestSnapshotBaseUrl`, `page.request` fetch, error-on-404, whole-block TODO placeholders (Task 4); test app + e2e test (Task 5); docs/quartodoc/controller-doc-test/CHANGELOG (Tasks 4 & 6).
- **Deferred (NOT in this plan):** B2 preprocessing, B4 query params, B3 `shiny-testmode.js`; whole-block `expect_*s` are commented placeholders only.
- **Type consistency:** controller methods are `expect_input/expect_output/expect_export(key, value, *, timeout=None)` and `get()`; the shared helper is `_expect_value(block, key, value, timeout)`; `env` parameter type is `dict[str, str] | None` everywhere; `_subprocess_env(env)` returns `dict[str, str] | None`.
- **Retry semantics:** `_fetch` raises `RuntimeError` on a non-OK response (misconfiguration → not retried); per-key mismatches/missing keys raise `AssertionError` (retried by `retry_with_timeout`).
