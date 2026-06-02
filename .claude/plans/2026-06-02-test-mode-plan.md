# Test Mode (Phase A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an R-Shiny-style "test mode" to py-shiny: an `SHINY_TESTMODE`-gated per-session JSON snapshot endpoint at `/session/{id}/dataobj/shinytest` returning `{input, output, export}`, plus an `export_test_values()` API for surfacing internal reactive values.

**Architecture:** A single env-var flag (`SHINY_TESTMODE`) read at `App.__init__` into `app._test_mode`. When on: the outbound message queue persistently records the last value/error of every output; a new request-handler branch serves a JSON snapshot built from inputs (`Inputs._serialize_test_mode`), recorded outputs, and lazily-evaluated registered exports; all serialized best-effort via `orjson` with sorted keys. When off: every piece is a no-op and the endpoint 404s.

**Tech Stack:** Python, Starlette (request/response), orjson (already a dependency), pytest + pytest-asyncio.

**Spec:** `.claude/plans/2026-06-02-test-mode-design.md` (Issue rstudio/py-shiny#2269).

---

## File Structure

- `shiny/_utils.py` — add `is_test_mode()` env-var helper.
- `shiny/_app.py` — read `is_test_mode()` into `self._test_mode`.
- `shiny/session/_session.py` — output recording in `OutBoundMessageQueues`; `export_test_values` + `get_test_snapshot_url` on `Session`/`AppSession`/`SessionProxy`; export registry; `Inputs._serialize_test_mode`; `_is_internal_snapshot_input`, `_snapshot_safe_value` module helpers; `dataobj/shinytest` branch + `_handle_test_snapshot`.
- `shiny/express/_stub_session.py` — no-op `export_test_values` / `get_test_snapshot_url`.
- `shiny/_export.py` — NEW: module-level `export_test_values()`.
- `shiny/__init__.py` — export `export_test_values`.
- `tests/pytest/test_test_mode.py` — NEW: all phase-A unit/integration tests.
- `docs/_quartodoc-core.yml`, `CHANGELOG.md` — docs.

---

## Task 1: `is_test_mode()` env-var helper

**Files:**
- Modify: `shiny/_utils.py`
- Test: `tests/pytest/test_test_mode.py` (create)

- [ ] **Step 1: Write the failing test**

Create `tests/pytest/test_test_mode.py`:

```python
"""Tests for Shiny test mode (Phase A)."""

from __future__ import annotations

import pytest

from shiny._utils import is_test_mode


def test_is_test_mode_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    assert is_test_mode() is False

    monkeypatch.setenv("SHINY_TESTMODE", "1")
    assert is_test_mode() is True

    monkeypatch.setenv("SHINY_TESTMODE", "0")
    assert is_test_mode() is False

    monkeypatch.setenv("SHINY_TESTMODE", "true")
    assert is_test_mode() is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/pytest/test_test_mode.py::test_is_test_mode_reads_env -v`
Expected: FAIL with `ImportError: cannot import name 'is_test_mode'`.

- [ ] **Step 3: Implement `is_test_mode()`**

In `shiny/_utils.py`, first confirm `import os` is present near the top (it is used elsewhere; add `import os` to the stdlib import group if missing). Then add this function (place it just below the existing `rand_hex` function, around line 45):

```python
def is_test_mode() -> bool:
    """
    Whether Shiny test mode is enabled.

    Test mode is enabled by setting the ``SHINY_TESTMODE`` environment variable
    to ``"1"``. When enabled, each session records the last value of every output
    and serves a JSON snapshot endpoint at ``/session/{id}/dataobj/shinytest``.
    """
    return os.getenv("SHINY_TESTMODE") == "1"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/pytest/test_test_mode.py::test_is_test_mode_reads_env -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add shiny/_utils.py tests/pytest/test_test_mode.py
git commit -m "feat: Add is_test_mode() env-var helper for test mode (#2269)"
```

---

## Task 2: Read test-mode flag into `App._test_mode`

**Files:**
- Modify: `shiny/_app.py` (import + `__init__` around line 182)
- Test: `tests/pytest/test_test_mode.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/pytest/test_test_mode.py`:

```python
from shiny import App, ui


def test_app_reads_test_mode_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    app_on = App(ui.TagList(), None)
    assert app_on._test_mode is True

    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    app_off = App(ui.TagList(), None)
    assert app_off._test_mode is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/pytest/test_test_mode.py::test_app_reads_test_mode_flag -v`
Expected: FAIL with `AttributeError: 'App' object has no attribute '_test_mode'`.

- [ ] **Step 3: Implement the flag**

In `shiny/_app.py`, add `is_test_mode` to the existing `from ._utils import ...` import (or add `from ._utils import is_test_mode` near the other `._utils` imports). Then in `App.__init__`, immediately after the line `self._debug: bool = debug` (line 182), add:

```python
        self._test_mode: bool = is_test_mode()
        """Whether Shiny test mode is enabled (via the ``SHINY_TESTMODE`` env var)."""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/pytest/test_test_mode.py::test_app_reads_test_mode_flag -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add shiny/_app.py tests/pytest/test_test_mode.py
git commit -m "feat: Read SHINY_TESTMODE into App._test_mode (#2269)"
```

---

## Task 3: Persistent output recording in `OutBoundMessageQueues`

**Files:**
- Modify: `shiny/session/_session.py` (`OutBoundMessageQueues` class ~line 152; `AppSession.__init__` ~line 763)
- Test: `tests/pytest/test_test_mode.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/pytest/test_test_mode.py` (this also adds the shared helpers used by later tasks):

```python
from starlette.requests import Request

from shiny import reactive
from shiny._connection import MockConnection
from shiny.session._session import AppSession, OutBoundMessageQueues
from shiny.session._utils import session_context


def _make_app_session() -> AppSession:
    """Create a real AppSession backed by a MockConnection.

    Construct AFTER setting/clearing SHINY_TESTMODE so `app._test_mode` reflects
    the desired state.
    """
    conn = MockConnection()
    return App(ui.TagList(), None)._create_session(conn)


def _snapshot_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "headers": [],
            "query_string": b"",
            "path": "/",
        }
    )


def test_outbound_queue_records_when_on() -> None:
    omq = OutBoundMessageQueues(record_test_values=True)

    omq.set_value("out1", 42)
    omq.reset()  # a flush clears the transient queues...
    assert omq.test_values == {"out1": 42}  # ...but not the test record

    # set_error supersedes a recorded value for the same id
    omq.set_error("out1", {"message": "boom"})
    assert "out1" not in omq.test_values
    assert omq.test_errors == {"out1": {"message": "boom"}}

    # set_value supersedes a recorded error for the same id
    omq.set_value("out1", 7)
    assert omq.test_values == {"out1": 7}
    assert "out1" not in omq.test_errors


def test_outbound_queue_no_record_when_off() -> None:
    omq = OutBoundMessageQueues(record_test_values=False)
    omq.set_value("out1", 42)
    omq.set_error("out2", {"message": "boom"})
    assert omq.test_values == {}
    assert omq.test_errors == {}


def test_app_session_wires_record_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()
    assert session._outbound_message_queues._record_test_values is True

    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    session_off = _make_app_session()
    assert session_off._outbound_message_queues._record_test_values is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/pytest/test_test_mode.py -k outbound_queue -v`
Expected: FAIL with `TypeError: __init__() got an unexpected keyword argument 'record_test_values'`.

- [ ] **Step 3: Implement recording in the queue**

In `shiny/session/_session.py`, replace the `OutBoundMessageQueues` class (lines 152-176) with:

```python
class OutBoundMessageQueues:
    def __init__(self, record_test_values: bool = False):
        self.values: dict[str, Any] = {}
        self.errors: dict[str, Any] = {}
        self.input_messages: list[dict[str, Any]] = []

        # Test-mode (`SHINY_TESTMODE`) persistent record of the last value/error
        # sent for each output. Unlike `values`/`errors`, these are NOT cleared
        # by `reset()`, so a test snapshot can report the last computed value of
        # every output even though the transient queues are flushed each cycle.
        self._record_test_values = record_test_values
        self.test_values: dict[str, Any] = {}
        self.test_errors: dict[str, Any] = {}

    def reset(self) -> None:
        self.values.clear()
        self.errors.clear()
        self.input_messages.clear()

    def set_value(self, id: str, value: Any) -> None:
        self.values[id] = value
        # remove from self.errors
        if id in self.errors:
            del self.errors[id]
        if self._record_test_values:
            self.test_values[id] = value
            self.test_errors.pop(id, None)

    def set_error(self, id: str, error: Any) -> None:
        self.errors[id] = error
        # remove from self.values
        if id in self.values:
            del self.values[id]
        if self._record_test_values:
            self.test_errors[id] = error
            self.test_values.pop(id, None)

    def add_input_message(self, id: str, message: dict[str, Any]) -> None:
        self.input_messages.append({"id": id, "message": message})
```

Then in `AppSession.__init__`, replace line 763:

```python
        self._outbound_message_queues = OutBoundMessageQueues()
```

with:

```python
        self._outbound_message_queues = OutBoundMessageQueues(
            record_test_values=app._test_mode
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/pytest/test_test_mode.py -k "outbound_queue or wires_record" -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add shiny/session/_session.py tests/pytest/test_test_mode.py
git commit -m "feat: Record last output values/errors in test mode (#2269)"
```

---

## Task 4: `export_test_values()` session API + registry

**Files:**
- Modify: `shiny/session/_session.py` (`Session` ABC; `AppSession.__init__` registry + method; `SessionProxy` method)
- Modify: `shiny/express/_stub_session.py` (no-op)
- Test: `tests/pytest/test_test_mode.py`

> NOTE: This task adds a new `@abstractmethod` to `Session`. To keep every `Session` subclass instantiable, the abstract declaration AND all three concrete implementations (`AppSession`, `SessionProxy`, `ExpressStubSession`) must land together in this task.

- [ ] **Step 1: Write the failing test**

Append to `tests/pytest/test_test_mode.py`:

```python
def test_export_test_values_registers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    session.export_test_values(foo=lambda: 1, bar=lambda: 2)
    assert set(session._test_value_exports) == {"foo", "bar"}

    # last-registration-wins on duplicate name
    session.export_test_values(foo=lambda: 99)
    assert session._test_value_exports["foo"]() == 99


def test_export_test_values_noop_when_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    session = _make_app_session()
    session.export_test_values(foo=lambda: 1)
    assert session._test_value_exports == {}


def test_export_test_values_namespaced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    root = _make_app_session()
    proxy = root.make_scope("mod1")
    proxy.export_test_values(foo=lambda: 1)
    # DEVIATION from R: export names are namespaced with the module prefix.
    assert "mod1-foo" in root._test_value_exports
    assert "foo" not in root._test_value_exports
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/pytest/test_test_mode.py -k export_test_values -v`
Expected: FAIL with `AttributeError: 'AppSession' object has no attribute 'export_test_values'`.

- [ ] **Step 3a: Add the abstract method on `Session`**

In `shiny/session/_session.py`, add this `@abstractmethod` to the `Session` ABC, immediately after the `dynamic_route` abstract method (after line 575, before `set_message_handler` at line 577):

```python
    @abstractmethod
    def export_test_values(self, **kwargs: Callable[[], Any]) -> None:
        """
        Register named values to include in the test-mode snapshot.

        Each value must be a zero-argument callable (a plain function/`lambda` or
        a `reactive.calc`); it is evaluated lazily, in a reactive isolate, when a
        test snapshot is requested. Registered values appear under the ``export``
        block of the snapshot returned by the ``dataobj/shinytest`` endpoint.

        Has no effect unless test mode is enabled (``SHINY_TESTMODE=1``), so calls
        can be left in production code. Re-registering a name overwrites it.

        Parameters
        ----------
        **kwargs
            Named zero-argument callables whose return values are exported.

        See Also
        --------
        * :func:`~shiny.export_test_values`
        """
```

- [ ] **Step 3b: Add registry + method on `AppSession`**

In `AppSession.__init__`, immediately after line 769 (`self._dynamic_routes: dict[str, DynamicRouteHandler] = {}`), add:

```python
        # Test-mode (`SHINY_TESTMODE`) registry of values to include in the
        # `export` block of the snapshot. Keys are (namespaced) export names;
        # values are zero-arg callables evaluated lazily at snapshot time.
        self._test_value_exports: dict[str, Callable[[], Any]] = {}
```

Then add this method on `AppSession`, just after the `dynamic_route` method (after line 1430):

```python
    def export_test_values(self, **kwargs: Callable[[], Any]) -> None:
        if not self.app._test_mode:
            return
        self._test_value_exports.update(kwargs)
```

- [ ] **Step 3c: Add namespacing method on `SessionProxy`**

In `shiny/session/_session.py`, add this method to `SessionProxy`, just after its `dynamic_route` method (after line 1670):

```python
    def export_test_values(self, **kwargs: Callable[[], Any]) -> None:
        # NOTE: Deviation from R Shiny's `exportTestValues()`, which does NOT
        # namespace export names. py-shiny namespaces them with this module's
        # `ns` prefix so values exported from different modules don't collide.
        namespaced = {str(self.ns(name)): value for name, value in kwargs.items()}
        self._root_session.export_test_values(**namespaced)
```

- [ ] **Step 3d: Add no-op on `ExpressStubSession`**

In `shiny/express/_stub_session.py`, add this method just after the `dynamic_route` method (after line 140):

```python
    def export_test_values(self, **kwargs: Callable[[], Any]) -> None:
        return
```

(Confirm `Callable` and `Any` are imported in `_stub_session.py`; both are standard in that file's `typing` imports — add to the import if missing.)

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/pytest/test_test_mode.py -k export_test_values -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add shiny/session/_session.py shiny/express/_stub_session.py tests/pytest/test_test_mode.py
git commit -m "feat: Add session.export_test_values() with module namespacing (#2269)"
```

---

## Task 5: Module-level `export_test_values()` + top-level export

**Files:**
- Create: `shiny/_export.py`
- Modify: `shiny/__init__.py`
- Test: `tests/pytest/test_test_mode.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/pytest/test_test_mode.py`:

```python
def test_module_level_export_uses_current_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    from shiny import export_test_values

    session = _make_app_session()
    with session_context(session):
        export_test_values(foo=lambda: 1)
    assert "foo" in session._test_value_exports


def test_module_level_export_targets_other_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    from shiny import export_test_values

    other = _make_app_session()
    # No active session here; target `other` explicitly via its context.
    with session_context(other):
        export_test_values(bar=lambda: 2)
    assert "bar" in other._test_value_exports


def test_module_level_export_requires_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    from shiny import export_test_values

    with pytest.raises(ValueError):
        export_test_values(foo=lambda: 1)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/pytest/test_test_mode.py -k module_level_export -v`
Expected: FAIL with `ImportError: cannot import name 'export_test_values' from 'shiny'`.

- [ ] **Step 3a: Create `shiny/_export.py`**

```python
"""Test-mode value exporting (see `SHINY_TESTMODE`)."""

from __future__ import annotations

from typing import Any, Callable

from .session import require_active_session

__all__ = ("export_test_values",)


def export_test_values(**kwargs: Callable[[], Any]) -> None:
    """
    Register named values to include in the test-mode snapshot.

    This is the module-level counterpart to
    :meth:`shiny.Session.export_test_values`. It uses the current reactive
    session. Each value must be a zero-argument callable (a plain
    function/`lambda` or a `reactive.calc`); it is evaluated lazily, in a
    reactive isolate, when a test snapshot is requested. Registered values appear
    under the ``export`` block of the snapshot served at
    ``/session/{id}/dataobj/shinytest``.

    Has no effect unless test mode is enabled (``SHINY_TESTMODE=1``), so calls can
    be left in production code. Re-registering a name overwrites it.

    To register against a session other than the current one, wrap the call in
    that session's context:

    ```python
    from shiny.session import session_context

    with session_context(other_session):
        export_test_values(my_val=lambda: ...)
    ```

    Parameters
    ----------
    **kwargs
        Named zero-argument callables whose return values are exported.

    Raises
    ------
    ValueError
        If there is no active session.

    See Also
    --------
    * `shiny.Session.export_test_values`
    """
    session = require_active_session(None)
    session.export_test_values(**kwargs)
```

- [ ] **Step 3b: Export from `shiny/__init__.py`**

After the `from ._validation import req` line (line 21), add:

```python
from ._export import export_test_values
```

And in `__all__`, after `"req",` (line 62), add:

```python
    # _export.py
    "export_test_values",
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/pytest/test_test_mode.py -k module_level_export -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add shiny/_export.py shiny/__init__.py tests/pytest/test_test_mode.py
git commit -m "feat: Add top-level shiny.export_test_values() (#2269)"
```

---

## Task 6: Test-mode input serialization

**Files:**
- Modify: `shiny/session/_session.py` (add `_is_internal_snapshot_input` helper; refactor `Inputs._serialize` to use it; add `Inputs._serialize_test_mode`)
- Test: `tests/pytest/test_test_mode.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/pytest/test_test_mode.py`:

```python
def test_is_internal_snapshot_input() -> None:
    from shiny.session._session import _is_internal_snapshot_input

    assert _is_internal_snapshot_input(".clientdata_output_x_hidden") is True
    assert _is_internal_snapshot_input(".shinybookmarkstate") is False  # not the id
    assert _is_internal_snapshot_input("x") is False


def test_serialize_test_mode_collects_and_skips() -> None:
    from shiny.session._session import Inputs

    inputs = Inputs(dict())
    inputs["x"] = reactive.Value(5)
    inputs["name"] = reactive.Value("hi")
    inputs[".clientdata_output_x_hidden"] = reactive.Value(True)

    result = inputs._serialize_test_mode()
    assert result == {"x": 5, "name": "hi"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/pytest/test_test_mode.py -k "internal_snapshot_input or serialize_test_mode" -v`
Expected: FAIL with `ImportError`/`AttributeError` for `_is_internal_snapshot_input` / `_serialize_test_mode`.

- [ ] **Step 3a: Add the `_is_internal_snapshot_input` module helper**

In `shiny/session/_session.py`, add this function just above the `Inputs` class (before line 1701, after the `# Inputs` banner comment):

```python
def _is_internal_snapshot_input(key: str) -> bool:
    """
    Whether an input key is client-internal and excluded from snapshots.

    Used by both bookmark serialization and test-mode snapshots to skip
    client-data inputs (``.clientdata_*``) and the bookmark machinery inputs.
    """
    if key.startswith(".clientdata_"):
        return True
    if key == BOOKMARK_ID or key.endswith(f"{ResolvedId._sep}{BOOKMARK_ID}"):
        return True
    return False
```

- [ ] **Step 3b: Refactor `Inputs._serialize` to use the helper (behavior-preserving)**

In `Inputs._serialize` (lines 1841-1851), replace these lines:

```python
                # TODO: Barret - Q: Should this be ignoring any Input key that starts with a "."?
                if key.startswith(".clientdata_"):
                    continue
                # Ignore all bookmark inputs
                if key == BOOKMARK_ID or key.endswith(
                    f"{ResolvedId._sep}{BOOKMARK_ID}"
                ):
                    continue
                if key in exclude_set:
                    continue
```

with:

```python
                if _is_internal_snapshot_input(str(key)):
                    continue
                if key in exclude_set:
                    continue
```

- [ ] **Step 3c: Add `Inputs._serialize_test_mode`**

Add this method to the `Inputs` class, immediately after `_serialize` (after line 1867):

```python
    def _serialize_test_mode(self) -> dict[str, Any]:
        """
        Collect current input values for a test-mode snapshot.

        Unlike `_serialize` (used for bookmarking), this applies no bookmark
        serializers and never touches the filesystem; raw values are returned for
        best-effort JSON serialization by the snapshot handler. Client-internal
        and bookmark inputs are skipped.
        """
        out: dict[str, Any] = {}
        with reactive.isolate():
            for key, value in self._map.items():
                if _is_internal_snapshot_input(str(key)):
                    continue
                try:
                    val = value()
                except SilentException:
                    continue
                out[str(key)] = val
        return out
```

- [ ] **Step 4: Run tests to verify they pass (including no regression in bookmark serialization)**

Run: `pytest tests/pytest/test_test_mode.py -k "internal_snapshot_input or serialize_test_mode" -v`
Expected: PASS (2 tests).

Run the bookmark tests to confirm the `_serialize` refactor is behavior-preserving:
`pytest tests/pytest -k bookmark -q`
Expected: PASS (no new failures).

- [ ] **Step 5: Commit**

```bash
git add shiny/session/_session.py tests/pytest/test_test_mode.py
git commit -m "feat: Add Inputs._serialize_test_mode and shared skip helper (#2269)"
```

---

## Task 7: Best-effort snapshot value serialization

**Files:**
- Modify: `shiny/session/_session.py` (add `import orjson`; add `_snapshot_safe_value`)
- Test: `tests/pytest/test_test_mode.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/pytest/test_test_mode.py`:

```python
def test_snapshot_safe_value() -> None:
    from shiny.session._session import _snapshot_safe_value

    # JSON-native passes through
    assert _snapshot_safe_value({"a": 1, "b": [1, 2]}) == {"a": 1, "b": [1, 2]}

    # Non-native coerced via str()
    class Stringy:
        def __str__(self) -> str:
            return "stringy-value"

    assert _snapshot_safe_value(Stringy()) == "stringy-value"

    # Unconvertible -> visible, non-fatal marker
    class Bad:
        def __str__(self) -> str:
            raise RuntimeError("nope")

    out = _snapshot_safe_value(Bad())
    assert isinstance(out, dict)
    assert "__shiny_serialization_error__" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/pytest/test_test_mode.py -k snapshot_safe_value -v`
Expected: FAIL with `ImportError: cannot import name '_snapshot_safe_value'`.

- [ ] **Step 3: Implement the helper**

In `shiny/session/_session.py`, add `import orjson` to the stdlib/third-party import group near the top (after `import json` on line 9, in correct alphabetical/grouping order — orjson is third-party, place it with other third-party imports near `from starlette...`). Then add this module-level function just above the `_is_internal_snapshot_input` helper added in Task 6:

```python
def _snapshot_safe_value(value: Any) -> Any:
    """
    Coerce a value into something JSON-serializable for a test snapshot.

    Best-effort: values that orjson cannot encode are stringified via
    ``default=str``. If serialization still fails (e.g. ``str()`` raises), a
    visible, non-fatal marker is returned so a single bad value never fails the
    whole snapshot.
    """
    try:
        return orjson.loads(orjson.dumps(value, default=str))
    except Exception as e:
        return {"__shiny_serialization_error__": str(e)}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/pytest/test_test_mode.py -k snapshot_safe_value -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add shiny/session/_session.py tests/pytest/test_test_mode.py
git commit -m "feat: Add best-effort snapshot value serializer (#2269)"
```

---

## Task 8: `get_test_snapshot_url()`

**Files:**
- Modify: `shiny/session/_session.py` (`Session` ABC; `AppSession`; `SessionProxy`)
- Modify: `shiny/express/_stub_session.py`
- Test: `tests/pytest/test_test_mode.py`

> NOTE: Like Task 4, this adds a `@abstractmethod` to `Session`; declaration + all three implementations land together so every subclass stays instantiable.

- [ ] **Step 1: Write the failing test**

Append to `tests/pytest/test_test_mode.py`:

```python
def test_get_test_snapshot_url() -> None:
    session = _make_app_session()
    url = session.get_test_snapshot_url()
    assert url.startswith(f"session/{session.id}/dataobj/shinytest?nonce=")

    # Proxy delegates to the root session (no namespacing of the URL)
    proxy = session.make_scope("mod1")
    purl = proxy.get_test_snapshot_url()
    assert purl.startswith(f"session/{session.id}/dataobj/shinytest?nonce=")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/pytest/test_test_mode.py -k get_test_snapshot_url -v`
Expected: FAIL with `AttributeError: 'AppSession' object has no attribute 'get_test_snapshot_url'`.

- [ ] **Step 3a: Abstract method on `Session`**

In `shiny/session/_session.py`, add to the `Session` ABC, immediately after the `export_test_values` abstract method added in Task 4:

```python
    @abstractmethod
    def get_test_snapshot_url(self) -> str:
        """
        Return the URL of this session's test-mode snapshot endpoint.

        The URL (with a fresh cache-busting ``nonce``) points at the
        ``dataobj/shinytest`` endpoint, which returns a JSON snapshot of this
        session's ``input``, ``output``, and ``export`` values. The endpoint only
        responds when test mode is enabled (``SHINY_TESTMODE=1``); otherwise it
        returns a 404.

        Returns
        -------
        :
            The URL path for the snapshot endpoint.
        """
```

- [ ] **Step 3b: `AppSession` implementation**

Add this method to `AppSession`, immediately after its `export_test_values` method (added in Task 4):

```python
    def get_test_snapshot_url(self) -> str:
        nonce = _utils.rand_hex(8)
        return (
            f"session/{urllib.parse.quote(self.id)}"
            f"/dataobj/shinytest?nonce={urllib.parse.quote(nonce)}"
        )
```

- [ ] **Step 3c: `SessionProxy` implementation**

Add this method to `SessionProxy`, immediately after its `export_test_values` method (added in Task 4):

```python
    def get_test_snapshot_url(self) -> str:
        return self._root_session.get_test_snapshot_url()
```

- [ ] **Step 3d: `ExpressStubSession` implementation**

In `shiny/express/_stub_session.py`, add immediately after its `export_test_values` method (added in Task 4):

```python
    def get_test_snapshot_url(self) -> str:
        return ""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/pytest/test_test_mode.py -k get_test_snapshot_url -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add shiny/session/_session.py shiny/express/_stub_session.py tests/pytest/test_test_mode.py
git commit -m "feat: Add session.get_test_snapshot_url() (#2269)"
```

---

## Task 9: The `dataobj/shinytest` endpoint

**Files:**
- Modify: `shiny/session/_session.py` (`from starlette.responses import Response`; new branch in `_handle_request_impl`; `_handle_test_snapshot` method on `AppSession`)
- Test: `tests/pytest/test_test_mode.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/pytest/test_test_mode.py`:

```python
@pytest.mark.asyncio
async def test_snapshot_endpoint_returns_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    session.input["x"] = reactive.Value(10)
    session._outbound_message_queues.set_value("out1", "hello")
    session._outbound_message_queues.set_error("out2", {"message": "boom"})
    session.export_test_values(myexp=lambda: 123)

    resp = await session._handle_request_impl(
        _snapshot_request(), "dataobj", "shinytest"
    )
    import orjson

    body = orjson.loads(resp.body)

    assert body["input"]["x"] == 10
    assert body["output"]["out1"] == "hello"
    assert body["output"]["out2"] == {"__shiny_output_error__": "boom"}
    assert body["export"]["myexp"] == 123

    # OPT_SORT_KEYS -> top-level keys are emitted in sorted order
    assert list(body.keys()) == ["export", "input", "output"]


@pytest.mark.asyncio
async def test_snapshot_endpoint_404_when_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    session = _make_app_session()
    resp = await session._handle_request_impl(
        _snapshot_request(), "dataobj", "shinytest"
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_snapshot_endpoint_export_error_marker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    class Bad:
        def __str__(self) -> str:
            raise RuntimeError("nope")

    def raises() -> object:
        raise RuntimeError("export boom")

    session.export_test_values(bad_value=lambda: Bad(), raises=raises)

    resp = await session._handle_request_impl(
        _snapshot_request(), "dataobj", "shinytest"
    )
    import orjson

    body = orjson.loads(resp.body)
    assert "__shiny_serialization_error__" in body["export"]["bad_value"]
    assert "__shiny_serialization_error__" in body["export"]["raises"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/pytest/test_test_mode.py -k snapshot_endpoint -v`
Expected: FAIL — the `404_when_off` test currently passes only by accident (unknown action → 404), but `returns_state` FAILs because the `dataobj/shinytest` branch does not exist (falls through to the final 404, so `resp.body` is HTML and `orjson.loads` raises).

- [ ] **Step 3a: Import `Response`**

In `shiny/session/_session.py`, update the Starlette responses import (line 36) from:

```python
from starlette.responses import HTMLResponse, PlainTextResponse, StreamingResponse
```

to:

```python
from starlette.responses import (
    HTMLResponse,
    PlainTextResponse,
    Response,
    StreamingResponse,
)
```

- [ ] **Step 3b: Add the request-handler branch**

In `AppSession._handle_request_impl`, add this branch immediately after the `dynamic_route` branch (after line 1250, before the final `return HTMLResponse("<h1>Not Found</h1>", 404)`):

```python
        elif (
            action == "dataobj"
            and subpath == "shinytest"
            and request.method == "GET"
        ):
            if not self.app._test_mode:
                return HTMLResponse("<h1>Not Found</h1>", 404)
            return self._handle_test_snapshot(request)
```

- [ ] **Step 3c: Add the `_handle_test_snapshot` method**

Add this method to `AppSession`, just after `_handle_request_impl` (after line 1252):

```python
    def _handle_test_snapshot(self, request: Request) -> ASGIApp:
        with session_context(self):
            with isolate():
                inputs = {
                    key: _snapshot_safe_value(val)
                    for key, val in self.input._serialize_test_mode().items()
                }

                omq = self._outbound_message_queues
                outputs: dict[str, Any] = {
                    key: _snapshot_safe_value(val)
                    for key, val in omq.test_values.items()
                }
                for key, err in omq.test_errors.items():
                    message = err.get("message") if isinstance(err, dict) else str(err)
                    outputs[key] = {"__shiny_output_error__": message}

                exports: dict[str, Any] = {}
                for name, fn in self._test_value_exports.items():
                    try:
                        exports[name] = _snapshot_safe_value(fn())
                    except Exception as e:
                        exports[name] = {"__shiny_serialization_error__": str(e)}

        payload = {"input": inputs, "output": outputs, "export": exports}
        body = orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)
        return Response(content=body, media_type="application/json")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/pytest/test_test_mode.py -k snapshot_endpoint -v`
Expected: PASS (3 tests).

Then run the full test-mode file:
`pytest tests/pytest/test_test_mode.py -v`
Expected: PASS (all tests).

- [ ] **Step 5: Commit**

```bash
git add shiny/session/_session.py tests/pytest/test_test_mode.py
git commit -m "feat: Serve test-mode snapshot at dataobj/shinytest (#2269)"
```

---

## Task 10: Type check, docs, and changelog

**Files:**
- Modify: `docs/_quartodoc-core.yml`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Run formatter and type checker**

Run: `make check-types`
Expected: PASS (no new pyright errors). If `Callable`/`Any` imports are missing in any edited file, add them and re-run.

Run: `make format`
Expected: black/isort make no further changes (or auto-fix; re-stage if so).

- [ ] **Step 2: Add quartodoc entries**

In `docs/_quartodoc-core.yml`, in the `Session` page `contents:` list (around lines 277-288), add these entries. Put `export_test_values` after `session.require_active_session` (line 278), and the two `Session` methods alongside the other `session.Session.*` entries (after `session.Session.dynamic_route`, line 287):

```yaml
            - export_test_values
```

and

```yaml
            - session.Session.export_test_values
            - session.Session.get_test_snapshot_url
```

- [ ] **Step 3: Add the CHANGELOG entry**

In `CHANGELOG.md`, under `## [UNRELEASED]`, add a `### New features` section (create the header if absent) with:

```markdown
### New features

* Added experimental test mode, enabled with the `SHINY_TESTMODE=1` environment variable. When enabled, each session serves a JSON snapshot of its `input`, `output`, and `export` values at `/session/{id}/dataobj/shinytest` (URL available via `session.get_test_snapshot_url()`). App authors can surface internal reactive values with `shiny.export_test_values()` / `session.export_test_values()`. (#2269)
```

- [ ] **Step 4: Verify the docstring examples and full suite**

Run: `pytest tests/pytest/test_test_mode.py -v`
Expected: PASS.

Run (sanity, no regressions in session/bookmark areas):
`pytest tests/pytest -k "bookmark or session or modules" -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/_quartodoc-core.yml CHANGELOG.md
git commit -m "docs: Document test mode and export_test_values (#2269)"
```

---

## Self-Review Notes (for the implementer)

- **Spec coverage:** enable flag (T1-2), `export_test_values` API + namespacing (T4-5), output last-value/error recording (T3), input serialization (T6), orjson best-effort + sorted (T7, T9), endpoint + 404 (T9), URL helper (T8), docs/changelog (T10). All spec sections map to a task.
- **Deferred (NOT in this plan):** Playwright access, `shiny-testmode.js`, snapshot preprocessing, `format=rds`/selective-filter/`sortC` query params, `App(test_mode=...)` constructor arg.
- **Type consistency:** registry `self._test_value_exports: dict[str, Callable[[], Any]]`; queue fields `test_values`/`test_errors`/`_record_test_values`; helpers `_is_internal_snapshot_input`, `_snapshot_safe_value`; markers `__shiny_serialization_error__` (serialization) and `__shiny_output_error__` (errored output). These names are used identically across tasks.
- **Instantiability:** each abstract method added to `Session` (T4, T8) lands with `AppSession` + `SessionProxy` + `ExpressStubSession` implementations in the same task.
```
