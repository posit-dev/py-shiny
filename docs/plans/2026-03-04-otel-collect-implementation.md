# `otel.collect` Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `otel.collect` as a symmetric counterpart to `otel.suppress`, while ensuring infrastructure spans always read the env var and are never affected by either API.

**Architecture:** Split `get_level()` into two paths: a private `_get_env_level()` (env var only, for infrastructure spans) and the existing contextvar-aware `get_level()` (for reactive init-time capture). Add a `_Collect` singleton to `_decorators.py` mirroring `_Suppress` exactly but setting `ALL` instead of `NONE`.

**Tech Stack:** Python `contextvars`, `shiny.otel`, pytest

---

### Task 1: Add `_get_env_level()` to `_collect.py`

**Files:**
- Modify: `shiny/otel/_collect.py`
- Test: `tests/pytest/test_otel_collect.py`

**Background:** `get_level()` currently reads the contextvar first, then falls back to the env var. Infrastructure spans (`session.start`, `session.end`, `reactive_update`, etc.) need to always read only the env var — they must be unaffected by `otel.suppress` / `otel.collect`. Extract the env-var-only logic into a private helper `_get_env_level()`.

**Step 1: Write the failing test**

Add to `TestGetLevel` in `tests/pytest/test_otel_collect.py`:

```python
def test_get_env_level_ignores_contextvar(self, monkeypatch: pytest.MonkeyPatch):
    from shiny.otel._collect import _get_env_level

    monkeypatch.setenv("SHINY_OTEL_COLLECT", "session")
    _current_collect_level.set(None)

    with otel.suppress():
        # get_level() returns NONE (contextvar wins)
        assert otel.get_level() == OtelCollectLevel.NONE
        # _get_env_level() ignores contextvar, returns env var value
        assert _get_env_level() == OtelCollectLevel.SESSION

def test_get_env_level_defaults_to_all(self):
    from shiny.otel._collect import _get_env_level

    _current_collect_level.set(None)
    assert _get_env_level() == OtelCollectLevel.ALL
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/pytest/test_otel_collect.py::TestGetLevel -v
```
Expected: FAIL with `ImportError: cannot import name '_get_env_level'`

**Step 3: Add `_get_env_level()` to `_collect.py`**

Extract the env-var logic from `get_level()` into a private helper. In `shiny/otel/_collect.py`, add after the `_current_collect_level` declaration:

```python
def _get_env_level() -> OtelCollectLevel:
    """Read the collection level from the env var only, bypassing the contextvar.

    Used by infrastructure spans (session.start, session.end, reactive_update)
    that must not be affected by otel.suppress() or otel.collect().
    """
    env_level = os.getenv("SHINY_OTEL_COLLECT", "all").strip().upper()

    if env_level == "REACTIVE":
        env_level = "REACTIVITY"

    try:
        return OtelCollectLevel[env_level]
    except KeyError:
        import warnings

        warnings.warn(
            f"Invalid SHINY_OTEL_COLLECT value: {env_level}. "
            f"Valid values are: {', '.join(level.name.lower() for level in OtelCollectLevel)}. "
            f"Defaulting to 'all'.",
            UserWarning,
            stacklevel=2,
        )
        return OtelCollectLevel.ALL
```

Then simplify `get_level()` to call `_get_env_level()` as its fallback:

```python
def get_level() -> OtelCollectLevel:
    # ... (keep existing docstring) ...
    level = _current_collect_level.get()
    if level is not None:
        return level
    return _get_env_level()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/pytest/test_otel_collect.py::TestGetLevel -v
```
Expected: All PASS

**Step 5: Commit**

```bash
git add shiny/otel/_collect.py tests/pytest/test_otel_collect.py
git commit -m "refactor(otel): Extract _get_env_level() for infrastructure span isolation"
```

---

### Task 2: Wire infrastructure span callers to `_get_env_level()`

**Files:**
- Modify: `shiny/reactive/_core.py:180-183`
- Modify: `shiny/session/_session.py:598-602, 693-700`
- Modify: `shiny/bookmark/_bookmark.py:410-413, 452-456`

**Background:** Infrastructure spans currently call `shiny_otel_span(...)` without passing `collection_level`, so `shiny_otel_span` calls `get_level()` at runtime (which reads the contextvar). They need to pass `collection_level=_get_env_level()` so the contextvar is bypassed.

**Step 1: Write the failing test**

Add a new class to `tests/pytest/test_otel_collect.py`:

```python
class TestInfrastructureSpanIsolation:
    """Infrastructure spans must not be affected by otel.suppress / otel.collect."""

    def test_get_env_level_inside_suppress_returns_env_not_none(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        from shiny.otel._collect import _get_env_level

        monkeypatch.setenv("SHINY_OTEL_COLLECT", "reactive_update")
        _current_collect_level.set(None)

        with otel.suppress():
            assert otel.get_level() == OtelCollectLevel.NONE
            assert _get_env_level() == OtelCollectLevel.REACTIVE_UPDATE

    def test_get_env_level_inside_collect_returns_env_not_all(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        from shiny.otel._collect import _get_env_level

        monkeypatch.setenv("SHINY_OTEL_COLLECT", "session")
        _current_collect_level.set(None)

        # After adding otel.collect (Task 3), this will also verify collect
        # does not affect _get_env_level
        assert _get_env_level() == OtelCollectLevel.SESSION
```

**Step 2: Run test to verify it passes already** (these test `_get_env_level` directly, which exists after Task 1)

```bash
pytest tests/pytest/test_otel_collect.py::TestInfrastructureSpanIsolation -v
```
Expected: PASS (the tests validate the helper, not the callers yet)

**Step 3: Update `_core.py`**

In `shiny/reactive/_core.py`, add the import:

```python
from ..otel._collect import _get_env_level
```

Change the `flush()` span call at line ~180:

```python
async with shiny_otel_span(
    "reactive_update",
    required_level=OtelCollectLevel.REACTIVE_UPDATE,
    collection_level=_get_env_level(),
):
```

**Step 4: Update `_session.py`**

In `shiny/session/_session.py`, add to existing otel imports:

```python
from ..otel._collect import _get_env_level
```

Add `collection_level=_get_env_level()` to the `session.end` span (~line 598):

```python
async with shiny_otel_span(
    "session.end",
    attributes=get_session_id_attrs(self),
    required_level=OtelCollectLevel.SESSION,
    collection_level=_get_env_level(),
):
```

Add `collection_level=_get_env_level()` to the `session.start` span (~line 693):

```python
async with shiny_otel_span(
    "session.start",
    attributes=lambda: {
        **get_session_id_attrs(self),
        **extract_http_attributes(self.http_conn),
    },
    required_level=OtelCollectLevel.SESSION,
    collection_level=_get_env_level(),
):
```

**Step 5: Update `_bookmark.py`**

In `shiny/bookmark/_bookmark.py`, add to existing otel imports:

```python
from ..otel._collect import _get_env_level
```

Add `collection_level=_get_env_level()` to both bookmark span calls (~lines 410, 452).

**Step 6: Run full otel test suite**

```bash
pytest tests/pytest/test_otel_collect.py tests/pytest/test_otel_session.py tests/pytest/test_otel_reactive_flush.py -v
```
Expected: All PASS

**Step 7: Commit**

```bash
git add shiny/reactive/_core.py shiny/session/_session.py shiny/bookmark/_bookmark.py tests/pytest/test_otel_collect.py
git commit -m "refactor(otel): Wire infrastructure spans to _get_env_level(), isolating them from suppress/collect"
```

---

### Task 3: Add `_CollectContext`, `_Collect`, and `collect` singleton to `_decorators.py`

**Files:**
- Modify: `shiny/otel/_decorators.py`
- Test: `tests/pytest/test_otel_collect.py`

**Background:** `_Suppress` sets `NONE`; `_Collect` sets `ALL`. The implementation is symmetric. `_CollectContext` mirrors `_SuppressContext`. `_Collect` mirrors `_Suppress` with the same TypeError guards. The singleton is named `collect`.

**Step 1: Write the failing tests**

Add to `tests/pytest/test_otel_collect.py`:

```python
class TestCollectDecorator:
    """Tests for @otel.collect (no parens) as a function decorator."""

    def test_stamps_function_with_all_level(self):
        @otel.collect
        def my_func():
            return 42

        assert getattr(my_func, FUNC_ATTR_OTEL_COLLECT_LEVEL) == OtelCollectLevel.ALL
        assert my_func() == 42

    def test_preserves_function_name_and_docstring(self):
        @otel.collect
        def my_func():
            """My docstring."""
            pass

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My docstring."

    def test_rejects_calc_object(self):
        from shiny import reactive

        @reactive.calc
        def my_calc():
            return 1

        with pytest.raises(TypeError, match="@reactive.calc"):
            otel.collect(my_calc)  # type: ignore[arg-type]

    def test_rejects_effect_object(self):
        from shiny import reactive

        @reactive.effect
        def my_effect():
            pass

        with pytest.raises(TypeError, match="@reactive.effect"):
            otel.collect(my_effect)  # type: ignore[arg-type]

    def test_rejects_renderer_object(self):
        from shiny import render

        @render.text
        def my_text():
            return "hello"

        with pytest.raises(TypeError, match="render"):
            otel.collect(my_text)  # type: ignore[arg-type]


class TestCollectContextManager:
    """Tests for with otel.collect(): as a context manager."""

    def test_sets_all_level_inside_block(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "none")
        _current_collect_level.set(None)

        assert otel.get_level() == OtelCollectLevel.NONE

        with otel.collect():
            assert otel.get_level() == OtelCollectLevel.ALL

        assert otel.get_level() == OtelCollectLevel.NONE

    def test_restores_level_after_exception(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "none")
        _current_collect_level.set(None)
        original = otel.get_level()

        with pytest.raises(ValueError):
            with otel.collect():
                assert otel.get_level() == OtelCollectLevel.ALL
                raise ValueError("boom")

        assert otel.get_level() == original

    def test_nested_collect_inside_suppress(self):
        with patch_otel_tracing_state(tracing_enabled=True):
            with otel.suppress():
                assert otel.get_level() == OtelCollectLevel.NONE
                with otel.collect():
                    assert otel.get_level() == OtelCollectLevel.ALL
                assert otel.get_level() == OtelCollectLevel.NONE

    def test_nested_suppress_inside_collect(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "none")
        _current_collect_level.set(None)

        with otel.collect():
            assert otel.get_level() == OtelCollectLevel.ALL
            with otel.suppress():
                assert otel.get_level() == OtelCollectLevel.NONE
            assert otel.get_level() == OtelCollectLevel.ALL


class TestCollectIntegration:
    """Integration tests for otel.collect with the reactive system."""

    def test_reactive_value_captures_all_at_init(self, monkeypatch: pytest.MonkeyPatch):
        from shiny import reactive

        monkeypatch.setenv("SHINY_OTEL_COLLECT", "none")
        _current_collect_level.set(None)

        with patch_otel_tracing_state(tracing_enabled=True):
            with otel.collect():
                val = reactive.value(0)
                assert val._otel_level == OtelCollectLevel.ALL

    def test_calc_captures_all_level_from_decorator(self):
        from shiny import reactive

        with patch_otel_tracing_state(tracing_enabled=True):

            @reactive.calc
            @otel.collect
            def my_calc():
                return 42

            assert my_calc._otel_level == OtelCollectLevel.ALL

    def test_collect_stamps_function_used_with_calc(self):
        from shiny.otel._function_attrs import resolve_func_otel_level

        @otel.collect
        def plain_func():
            return 99

        assert resolve_func_otel_level(plain_func) == OtelCollectLevel.ALL
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/pytest/test_otel_collect.py::TestCollectDecorator tests/pytest/test_otel_collect.py::TestCollectContextManager tests/pytest/test_otel_collect.py::TestCollectIntegration -v
```
Expected: FAIL with `AttributeError: module 'shiny.otel' has no attribute 'collect'`

**Step 3: Implement in `_decorators.py`**

In `shiny/otel/_decorators.py`, add after `_SuppressContext`:

```python
class _CollectContext:
    """Per-use context manager returned by collect(). Owns its own Token."""

    def __init__(self) -> None:
        self._token: Token[OtelCollectLevel | None] | None = None

    def __enter__(self) -> None:
        self._token = _current_collect_level.set(OtelCollectLevel.ALL)
        return None

    def __exit__(self, *_: object) -> None:
        if self._token is not None:
            _current_collect_level.reset(self._token)
            self._token = None
```

Add after the `_Suppress` class:

```python
class _Collect:
    """
    Singleton that enables Shiny's internal OTel instrumentation.

    Use as a no-parens decorator or a parens context manager:

        @reactive.calc
        @otel.collect
        def instrumented_calc(): ...

        with otel.collect():
            @reactive.effect
            def my_effect(): ...
    """

    @overload
    def __call__(self, func: T) -> T: ...  # @otel.collect

    @overload
    def __call__(self) -> _CollectContext: ...  # with otel.collect():

    def __call__(self, func: Any = None) -> Any:
        if func is None:
            return _CollectContext()

        from shiny.reactive._reactives import Calc_, Effect_
        from shiny.render.renderer import Renderer

        if isinstance(func, Calc_):
            raise TypeError(
                "otel.collect cannot be used on @reactive.calc objects. "
                "Apply @otel.collect before @reactive.calc:\n"
                "  @reactive.calc\n"
                "  @otel.collect\n"
                "  def my_calc(): ..."
            )

        if isinstance(func, Effect_):
            raise TypeError(
                "otel.collect cannot be used on @reactive.effect objects. "
                "Apply @otel.collect before @reactive.effect:\n"
                "  @reactive.effect\n"
                "  @otel.collect\n"
                "  def my_effect(): ..."
            )

        if isinstance(func, Renderer):
            raise TypeError(
                "otel.collect cannot be used on render objects. "
                "Apply @otel.collect before the @render.func decorator:\n"
                "  @render.text\n"
                "  @otel.collect\n"
                "  def my_output(): ..."
            )

        if not callable(func):
            raise TypeError(
                f"otel.collect received a non-callable argument: {type(func).__name__!r}. "
                f"Use @otel.collect (no parens) as a decorator, "
                f"or otel.collect() (with parens) as a context manager."
            )

        set_otel_collect_level_on_func(func, OtelCollectLevel.ALL)
        return func


collect = _Collect()
"""
Enables Shiny's internal telemetry for a function or block.

Use as a no-parens decorator:

    @reactive.calc
    @otel.collect
    def instrumented_calc(): ...

Use as a context manager (parens required):

    with otel.collect():
        @reactive.effect
        def my_effect(): ...

Note: This only affects Shiny's internal spans and logs. Your own custom
OpenTelemetry spans and logs are unaffected.
"""
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/pytest/test_otel_collect.py -v
```
Expected: All PASS

**Step 5: Commit**

```bash
git add shiny/otel/_decorators.py tests/pytest/test_otel_collect.py
git commit -m "feat(otel): Add otel.collect counterpart to otel.suppress"
```

---

### Task 4: Export `collect` from `__init__.py` and update docstring

**Files:**
- Modify: `shiny/otel/__init__.py`

**Background:** `collect` must be exported alongside `suppress` and `get_level`. The module docstring's "Programmatic Control" section needs a `otel.collect` example. The one-liner descriptions for both APIs should use the approved phrasing.

**Step 1: Update exports in `__init__.py`**

In `shiny/otel/__init__.py`, update the import and `__all__`:

```python
from ._collect import get_level
from ._decorators import collect, suppress

__all__ = (
    "collect",
    "get_level",
    "suppress",
)
```

**Step 2: Update the Quick Start example** in the module docstring to show both APIs:

```python
def server(input, output, session):
    @render.text
    def result():
        # Enables Shiny's internal telemetry for this output
        return f"Value: {input.n()}"

    @render.text
    @otel.suppress  # Disables Shiny's internal telemetry for sensitive operations
    def result_private():
        return f"Private value: {input.n()}"

    @render.text
    @otel.collect  # Enables Shiny's internal telemetry even when default is suppressed
    def result_instrumented():
        return f"Instrumented value: {input.n()}"
```

**Step 3: Add `otel.collect` to the "Programmatic Control" section**

After the existing `otel.suppress` Decorator and Context Manager subsections, add:

````markdown
### `otel.collect` Decorator

Use `otel.collect` as a decorator to enable Shiny's internal telemetry for a reactive function
when the default level is suppressed:

```python
from shiny import otel

@reactive.calc
@otel.collect
def instrumented_computation():
    """This calc always runs with Shiny telemetry, regardless of context."""
    return load_public_data()
```

### `otel.collect` Context Manager (Initialization Time Only)

Use `otel.collect()` as a context manager to enable telemetry during reactive object creation.
Any reactive objects defined inside the `with` block will have telemetry enabled:

```python
from shiny import otel

with otel.suppress():
    # Reactive objects created here have telemetry suppressed

    with otel.collect():
        @reactive.calc
        def public_calc():
            # This calc has telemetry enabled despite the outer suppress
            return load_public_data()

    @reactive.calc
    def private_calc():
        # Back to suppressed
        return load_private_data()
```
````

**Step 4: Update the "Sensitive Data in Traces" troubleshooting entry**

Add a note that `otel.collect` can re-enable for specific calcs inside a broad suppress block.

**Step 5: Run the full otel test suite**

```bash
pytest tests/pytest/test_otel*.py -v
```
Expected: All PASS

**Step 6: Commit**

```bash
git add shiny/otel/__init__.py
git commit -m "docs(otel): Export otel.collect and update module docstring"
```

---

### Task 5: Update example app and README

**Files:**
- Modify: `examples/open-telemetry/app.py`
- Modify: `examples/open-telemetry/README.md`

**Background:** The example app currently only demonstrates `otel.suppress`. Add a third card showing `otel.collect` overriding a low global default to demonstrate the counterpart.

**Step 1: Add `otel.collect` import to `app.py`**

The `from shiny import App, otel, reactive, render, ui` line already imports `otel`, so `otel.collect` is available.

**Step 2: Add a third column to the layout**

Add a third card to `ui.layout_columns(...)` in `app_ui`:

```python
ui.card(
    ui.card_header("Forced Telemetry (otel.collect)"),
    ui.input_slider("collect_slider", "Slider", 0, 100, 50),
    ui.input_action_button("collect_increment", "Increment Counter"),
    ui.output_text_verbatim("collect_counter_display"),
    ui.markdown("""
        **Telemetry:** ✅ Shiny spans + value logs
        Uses `@otel.collect` to enable Shiny telemetry even when
        the default level would otherwise suppress it.
        """),
),
```

**Step 3: Add server-side logic for the third card**

Inside `otel.suppress()` block (to simulate a low-default context), add:

```python
with otel.suppress():
    # ... existing private_counter code ...

    with otel.collect():
        # Demonstrates re-enabling within a suppressed context
        collect_counter = reactive.value(0)

        @reactive.effect
        @reactive.event(input.collect_increment)
        def _():
            collect_counter.set(collect_counter.get() + 1)
            print(f"\n>>> Collect counter updated to: {collect_counter.get()} (TELEMETRY ENABLED)")

        @render.text
        def collect_counter_display():
            slider_val = input.collect_slider()
            counter_val = collect_counter()
            return f"Slider: {slider_val}\nCounter: {counter_val}\n\n✅ Shiny telemetry re-enabled"
```

**Step 4: Update the README**

In `examples/open-telemetry/README.md`, add a new subsection under "Features Demonstrated":

```markdown
### 4. `otel.collect` Usage

```python
from shiny import otel

with otel.suppress():
    with otel.collect():
        @reactive.calc
        def public_within_private():
            # Telemetry enabled despite outer suppress
            return load_public_data()
```
```

Also update the Overview table to include `otel.collect`:

```markdown
| `otel.suppress` | Disables Shiny's internal telemetry |
| `otel.collect`  | Enables Shiny's internal telemetry  |
```

**Step 5: Manually verify the app runs**

```bash
cd examples/open-telemetry
SHINY_OTEL_COLLECT=all python app.py
```

Interact with all three cards and confirm the console shows spans for the Normal and Collect cards but not the Suppressed card.

**Step 6: Commit**

```bash
git add examples/open-telemetry/app.py examples/open-telemetry/README.md
git commit -m "docs(otel): Add otel.collect demonstration to open-telemetry example"
```

---

### Task 6: Run full test suite and verify

**Step 1: Run all otel tests**

```bash
pytest tests/pytest/test_otel*.py -v
```
Expected: All PASS

**Step 2: Run type checker**

```bash
make check-types
```
Expected: No new errors

**Step 3: Run formatter**

```bash
make format
```

**Step 4: Commit any formatting fixes**

```bash
git add -u
git commit -m "style: Apply black formatting to otel.collect changes"
```
