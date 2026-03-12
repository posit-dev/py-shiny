# Suppress Internal OTel Reactive Primitives — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Suppress OTel spans and value logs for internal reactive primitives in `_data_frame.py` and `_extended_task.py` that are implementation details users would never want to see in traces.

**Architecture:** Three independent, targeted changes using `with otel.suppress():` (for eagerly-created primitives) and `@otel.suppress` (for `@reactive_calc_method` functions, whose `Calc_` is created lazily — the suppression level propagates through `@wraps`). No API changes.

**Tech Stack:** Python, `shiny.otel`, `shiny.reactive`, pytest

---

### Task 1: Suppress `_data_frame.py` `_init_reactives()` internal primitives

**Files:**
- Modify: `shiny/render/_data_frame.py:11` (imports)
- Modify: `shiny/render/_data_frame.py:564-589` (`_init_reactives` method)
- Test: `tests/pytest/test_otel_data_frame.py` (new file)

**Step 1: Write the failing test**

Create `tests/pytest/test_otel_data_frame.py`:

```python
"""OTel suppression tests for DataFrame internal reactive primitives."""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from shiny.otel._collect import OtelCollectLevel
from shiny.render._data_frame import DataFrameT

from .otel_helpers import patch_otel_tracing_state


class TestDataFrameInitReactivesSuppressed:
    """Internal primitives in _init_reactives() are suppressed from OTel."""

    def test_internal_effect_otel_level_is_none(self):
        """The cell-style-update effect inside _init_reactives has OtelCollectLevel.NONE."""
        import shiny.reactive._reactives as reactives_mod

        captured_effects: list = []
        original_init = reactives_mod.Effect_.__init__

        def capturing_init(self, fn, *, session=None, **kwargs):
            original_init(self, fn, session=session, **kwargs)
            captured_effects.append(self)

        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                with patch.object(reactives_mod.Effect_, "__init__", capturing_init):
                    from shiny.render._data_frame import RenderDataFrame

                    mock_session = Mock()
                    mock_session.ns = lambda x: x
                    mock_session.id = "test-session"

                    renderer = RenderDataFrame.__new__(RenderDataFrame)
                    renderer._session = mock_session
                    renderer._init_reactives()

        # At least one Effect_ was created; all internal ones should be NONE
        assert len(captured_effects) >= 1
        for effect in captured_effects:
            assert effect._otel_level == OtelCollectLevel.NONE, (
                f"Expected NONE but got {effect._otel_level} for {effect}"
            )
```

**Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/pytest/test_otel_data_frame.py::TestDataFrameInitReactivesSuppressed -v
```

Expected: FAIL — effect has a non-NONE level.

**Step 3: Add `otel` import to `_data_frame.py`**

In `shiny/render/_data_frame.py`, change line 11:

```python
# Before
from .. import reactive, ui

# After
from .. import otel, reactive, ui
```

**Step 4: Wrap `_init_reactives()` body in `with otel.suppress():`**

In `shiny/render/_data_frame.py`, replace the `_init_reactives` method body:

```python
def _init_reactives(self) -> None:
    with otel.suppress():
        # Init
        self._value = reactive.Value(None)
        self._cell_patch_map = reactive.Value({})
        self._updated_data = reactive.Value()  # Create with no value

        # Update the styles any time the cell patch map or new data updates
        def should_update_styles():
            return (
                self._cell_patch_map(),
                # If the udpated data is unset, use a `None` value which is not allowed.
                self._updated_data() if self._updated_data.is_set() else None,
            )

        @reactive.effect
        @reactive.event(
            should_update_styles,
            # Do not run the first time through!
            # The styles are being sent with the initial blob.
            ignore_init=True,
        )
        async def _():
            # Be sure this is called within `isolate()` to isolate any reactivity
            # It currently is, as `@reactive.event()` is being used
            await self._attempt_update_cell_style()
```

**Step 5: Run test to verify it passes**

```bash
.venv/bin/pytest tests/pytest/test_otel_data_frame.py::TestDataFrameInitReactivesSuppressed -v
```

Expected: PASS.

**Step 6: Commit**

```bash
git add shiny/render/_data_frame.py tests/pytest/test_otel_data_frame.py
git commit -m "fix(otel): suppress internal reactives in DataFrame._init_reactives"
```

---

### Task 2: Suppress private `@reactive_calc_method` calcs in `_data_frame.py`

**Files:**
- Modify: `shiny/render/_data_frame.py` (4 private method definitions)
- Modify: `shiny/render/_data_frame_utils/_reactive_method.py:11` (add otel import)
- Test: `tests/pytest/test_otel_data_frame.py` (add new test class)

**Background:** `reactive_calc_method` creates a `Calc_` lazily (on first call). The level is resolved via `resolve_func_otel_level(fn)` at Calc_ creation time. `@otel.suppress` stamps `fn._shiny_otel_collect_level = NONE`, and `@wraps(fn)` inside `reactive_calc_method` copies this to the inner `calc_fn`. So the decorator order is:

```python
@reactive_calc_method   # outer — wraps the stamped fn
@otel.suppress          # stamps the function attribute
def _private(self): ...
```

**Step 1: Write the failing tests**

Add to `tests/pytest/test_otel_data_frame.py`:

```python
class TestDataFramePrivateCalcsSuppressed:
    """Private @reactive_calc_method calcs have OtelCollectLevel.NONE."""

    def _make_renderer(self):
        """Create a minimal RenderDataFrame instance for inspection."""
        from shiny.render._data_frame import RenderDataFrame
        renderer = RenderDataFrame.__new__(RenderDataFrame)
        renderer._session = None
        return renderer

    def test_private_nw_data_otel_level_is_none(self):
        """_nw_data calc has NONE level."""
        from shiny.otel._collect import OtelCollectLevel
        renderer = self._make_renderer()
        # Force lazy Calc_ creation by calling the method once (needs minimal setup)
        # Check via the Calc_ stored in __dict__
        # Access internal _reactive_calc_method cache via the class method wrapper
        from shiny.render._data_frame_utils._reactive_method import reactive_calc_method
        from shiny.render._data_frame import RenderDataFrame
        # The otel level is stamped on the function itself before Calc_ creation
        fn = RenderDataFrame._nw_data.__wrapped__ if hasattr(RenderDataFrame._nw_data, "__wrapped__") else RenderDataFrame._nw_data
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) == OtelCollectLevel.NONE

    def test_private_nw_data_patched_otel_level_is_none(self):
        from shiny.otel._collect import OtelCollectLevel
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.render._data_frame import RenderDataFrame
        fn = RenderDataFrame._nw_data_patched
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) == OtelCollectLevel.NONE

    def test_private_data_view_all_otel_level_is_none(self):
        from shiny.otel._collect import OtelCollectLevel
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.render._data_frame import RenderDataFrame
        fn = RenderDataFrame._data_view_all
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) == OtelCollectLevel.NONE

    def test_private_data_view_selected_otel_level_is_none(self):
        from shiny.otel._collect import OtelCollectLevel
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.render._data_frame import RenderDataFrame
        fn = RenderDataFrame._data_view_selected
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) == OtelCollectLevel.NONE

    def test_public_data_otel_level_unset(self):
        """Public .data() calc has NO suppression attribute (inherits ambient level)."""
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.render._data_frame import RenderDataFrame
        fn = RenderDataFrame.data
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) is None

    def test_public_cell_patches_otel_level_unset(self):
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.render._data_frame import RenderDataFrame
        fn = RenderDataFrame.cell_patches
        assert getattr(fn, FUNC_ATTR_OTEL_COLLECT_LEVEL, None) is None
```

**Step 2: Run tests to verify they fail**

```bash
.venv/bin/pytest tests/pytest/test_otel_data_frame.py::TestDataFramePrivateCalcsSuppressed -v
```

Expected: FAIL — private methods have no suppression attribute yet.

**Step 3: Add `@otel.suppress` to the four private methods in `_data_frame.py`**

Locate each private `@reactive_calc_method` definition and add `@otel.suppress` below it. The `otel` import added in Task 1 covers this.

```python
# _nw_data (around line 244)
@reactive_calc_method
@otel.suppress
def _nw_data(self) -> DataFrame[IntoDataFrameT]:
    ...

# _nw_data_patched (around line 332)
@reactive_calc_method
@otel.suppress
def _nw_data_patched(self) -> DataFrame[IntoDataFrameT]:
    ...

# _data_view_all (around line 407)
@reactive_calc_method
@otel.suppress
def _data_view_all(self) -> IntoDataFrameT:
    ...

# _data_view_selected (around line 419)
@reactive_calc_method
@otel.suppress
def _data_view_selected(self) -> IntoDataFrameT:
    ...
```

**Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/pytest/test_otel_data_frame.py::TestDataFramePrivateCalcsSuppressed -v
```

Expected: PASS.

**Step 5: Commit**

```bash
git add shiny/render/_data_frame.py tests/pytest/test_otel_data_frame.py
git commit -m "fix(otel): suppress private reactive_calc_method calcs in DataFrame"
```

---

### Task 3: Suppress `ExtendedTask` internal `Value` objects

**Files:**
- Modify: `shiny/reactive/_extended_task.py:83-104` (3 Value creations)
- Modify: `shiny/reactive/_extended_task.py` (add otel import)
- Test: `tests/pytest/test_otel_reactive_execution.py` (add to existing `TestExtendedTaskSpans`)

**Step 1: Write the failing test**

Add to `tests/pytest/test_otel_reactive_execution.py` inside `TestExtendedTaskSpans`:

```python
@pytest.mark.asyncio
async def test_extended_task_internal_values_do_not_log(self):
    """ExtendedTask status/value/error Values do not emit OTel logs."""
    import asyncio

    from shiny.reactive import ExtendedTask, isolate
    from shiny.otel._collect import OtelCollectLevel

    async def my_task():
        await asyncio.sleep(0)
        return 42

    task = ExtendedTask(my_task)

    # All three internal Values should have NONE level
    assert task.status._otel_level == OtelCollectLevel.NONE, (
        f"status._otel_level should be NONE, got {task.status._otel_level}"
    )
    assert task.value._otel_level == OtelCollectLevel.NONE, (
        f"value._otel_level should be NONE, got {task.value._otel_level}"
    )
    assert task.error._otel_level == OtelCollectLevel.NONE, (
        f"error._otel_level should be NONE, got {task.error._otel_level}"
    )
```

**Note:** Check that `reactive.Value` has an `_otel_level` attribute. If it doesn't, the test should instead verify no log is emitted when the value is set (use the `otel_log_provider_and_exporter` fixture from `test_otel_value_logging.py`).

**Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/pytest/test_otel_reactive_execution.py::TestExtendedTaskSpans::test_extended_task_internal_values_do_not_log -v
```

Expected: FAIL — Values don't have NONE level yet.

**Step 3: Add `otel` import and wrap Values in `_extended_task.py`**

In `shiny/reactive/_extended_task.py`, the existing imports use `from ..otel.*` style. Add:

```python
# Add to existing imports (around line 8, with other shiny imports)
from .. import otel
```

Then wrap the three Value creations (lines ~83-104). Keep all the preceding OTel label/level setup lines **outside** the suppress block:

```python
# Extract collection level from function attribute
self._otel_level: OtelCollectLevel = resolve_func_otel_level(func)

with otel.suppress():
    self.status: Value[Status] = Value("initial")
    """..."""

    self.value: Value[R] = Value()
    """..."""

    self.error: Value[BaseException] = Value()
    """..."""
```

**Step 4: Run test to verify it passes**

```bash
.venv/bin/pytest tests/pytest/test_otel_reactive_execution.py::TestExtendedTaskSpans::test_extended_task_internal_values_do_not_log -v
```

Expected: PASS.

**Step 5: Run the full OTel test suite to check for regressions**

```bash
.venv/bin/pytest tests/pytest/test_otel_*.py -v
```

Expected: All existing tests pass.

**Step 6: Commit**

```bash
git add shiny/reactive/_extended_task.py tests/pytest/test_otel_reactive_execution.py
git commit -m "fix(otel): suppress internal Values in ExtendedTask"
```

---

### Task 4: Final regression check

**Step 1: Run all unit tests**

```bash
.venv/bin/pytest tests/pytest/ -v
```

Expected: All pass.

**Step 2: Run formatting**

```bash
make format
```

**Step 3: Run type checking**

```bash
make check-types
```

Fix any type errors before proceeding.

**Step 4: Final commit if formatting changed anything**

```bash
git add -u
git commit -m "style: format after otel suppress additions"
```
