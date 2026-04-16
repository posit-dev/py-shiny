"""Tests for reactive destroy behavior."""

from __future__ import annotations

import asyncio
import gc
import weakref
from typing import Any, cast

import pytest

from shiny import _utils
from shiny._namespaces import ResolvedId
from shiny.express._stub_session import ExpressStubSession
from shiny.reactive import Value, calc, effect, flush, invalidate_later, isolate
from shiny.reactive._reactives import DestroyedReactiveError, Effect_
from shiny.render.renderer import Renderer
from shiny.session._session import (
    AppSession,
    Inputs,
    OutputInfo,
    Outputs,
    Session,
    SessionProxy,
)
from shiny.session._utils import session_context


def test_destroyed_reactive_error_is_exception():
    assert issubclass(DestroyedReactiveError, Exception)
    err = DestroyedReactiveError("test message")
    assert str(err) == "test message"


@pytest.mark.asyncio
async def test_value_destroy_raises_on_access():
    """After destroy(), get/set/unset/freeze raise DestroyedReactiveError."""
    v = Value(42)
    with isolate():
        assert v.is_set() is True
    v.destroy()
    # is_set() returns False (not an error — allows defensive checks)
    with isolate():
        assert v.is_set() is False
    # get() raises
    with pytest.raises(DestroyedReactiveError):
        with isolate():
            v()
    # set() raises
    with pytest.raises(DestroyedReactiveError):
        v.set(99)
    # unset() raises (calls set())
    with pytest.raises(DestroyedReactiveError):
        v.unset()
    # freeze() raises
    with pytest.raises(DestroyedReactiveError):
        v.freeze()


@pytest.mark.asyncio
async def test_value_destroy_invalidates_value_dependents():
    """destroy() invalidates downstream value dependents."""
    v = Value(10)
    call_count = 0

    @effect()
    def _():
        nonlocal call_count
        try:
            v()
        except Exception:
            pass
        call_count += 1

    await flush()
    assert call_count == 1

    v.destroy()
    await flush()
    assert call_count == 2


@pytest.mark.asyncio
async def test_value_destroy_invalidates_is_set_dependents():
    """destroy() invalidates is_set() dependents."""
    v = Value(10)
    is_set_results: list[bool] = []

    @effect()
    def _():
        is_set_results.append(v.is_set())

    await flush()
    assert is_set_results == [True]

    v.destroy()
    await flush()
    assert is_set_results == [True, False]


@pytest.mark.asyncio
async def test_value_destroy_is_idempotent():
    """Second destroy() call is a no-op."""
    v = Value(42)
    call_count = 0

    @effect()
    def _():
        nonlocal call_count
        try:
            v()
        except Exception:
            pass
        call_count += 1

    await flush()
    assert call_count == 1

    v.destroy()
    await flush()
    assert call_count == 2

    # Second destroy should NOT invalidate again
    v.destroy()
    await flush()
    assert call_count == 2


@pytest.mark.asyncio
async def test_value_destroy_works_on_read_only():
    """destroy() works on read-only values (input values)."""
    v = Value(42, read_only=True)
    with isolate():
        assert v.is_set() is True
    v.destroy()
    with isolate():
        assert v.is_set() is False


@pytest.mark.asyncio
async def test_calc_destroy_raises_on_subsequent_call():
    """After destroy(), calling the calc raises DestroyedReactiveError."""
    v = Value(10)

    @calc()
    def doubled():
        return v() * 2

    with isolate():
        assert doubled() == 20

    doubled.destroy()

    with pytest.raises(DestroyedReactiveError, match="has been destroyed"):
        doubled()


@pytest.mark.asyncio
async def test_calc_destroy_invalidates_context():
    """destroy() invalidates the calc's current context (breaks upstream)."""
    v = Value(10)

    @calc()
    def doubled():
        return v() * 2

    # Force evaluation to create the context
    with isolate():
        assert doubled() == 20

    # After destroy, changing v should NOT cause calc to re-register
    doubled.destroy()
    v.set(20)
    await flush()


@pytest.mark.asyncio
async def test_calc_destroy_invalidates_downstream_dependents():
    """destroy() invalidates downstream dependents of the calc."""
    v = Value(10)

    @calc()
    def doubled():
        return v() * 2

    results: list[int | str] = []

    @effect()
    def _():
        try:
            results.append(doubled())
        except DestroyedReactiveError:
            results.append("destroyed")

    await flush()
    assert results == [20]

    doubled.destroy()
    await flush()
    assert results == [20, "destroyed"]


@pytest.mark.asyncio
async def test_calc_destroy_is_idempotent():
    """Second destroy() call is a no-op."""
    v = Value(10)

    @calc()
    def doubled():
        return v() * 2

    with isolate():
        assert doubled() == 20

    doubled.destroy()
    doubled.destroy()  # Should not raise

    with pytest.raises(DestroyedReactiveError):
        doubled()


@pytest.mark.asyncio
async def test_calc_async_destroy():
    """Async calc destroy behaves the same as sync."""
    v = Value(10)

    @calc()
    async def doubled():
        return v() * 2

    with isolate():
        result = await doubled()
    assert result == 20

    doubled.destroy()

    with pytest.raises(DestroyedReactiveError, match="has been destroyed"):
        await doubled()


def test_inputs_destroy_removes_namespaced_keys():
    """destroy() removes all keys matching the namespace prefix."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    shared_map["panel_1-txt"] = Value("hello", read_only=True)
    shared_map["panel_1-slider"] = Value(5, read_only=True)
    shared_map["other-txt"] = Value("keep", read_only=True)

    inputs._destroy()

    assert "panel_1-txt" not in shared_map
    assert "panel_1-slider" not in shared_map
    assert "other-txt" in shared_map


def test_inputs_destroy_removes_clientdata_keys():
    """_destroy() removes per-output clientdata keys matching the namespace."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    shared_map[".clientdata_output_panel_1-my_plot_hidden"] = Value(
        False, read_only=True
    )
    shared_map[".clientdata_output_panel_1-my_plot_width"] = Value(800, read_only=True)
    shared_map[".clientdata_output_panel_1-my_plot_height"] = Value(600, read_only=True)

    inputs._destroy()

    assert ".clientdata_output_panel_1-my_plot_hidden" not in shared_map
    assert ".clientdata_output_panel_1-my_plot_width" not in shared_map
    assert ".clientdata_output_panel_1-my_plot_height" not in shared_map


def test_inputs_destroy_preserves_global_clientdata():
    """_destroy() does NOT remove global clientdata keys."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    shared_map[".clientdata_pixelratio"] = Value(2.0, read_only=True)
    shared_map[".clientdata_url_protocol"] = Value("https:", read_only=True)
    shared_map[".clientdata_singletons"] = Value("", read_only=True)
    shared_map["panel_1-txt"] = Value("remove me", read_only=True)

    inputs._destroy()

    assert ".clientdata_pixelratio" in shared_map
    assert ".clientdata_url_protocol" in shared_map
    assert ".clientdata_singletons" in shared_map
    assert "panel_1-txt" not in shared_map


def test_inputs_destroy_preserves_other_namespaces():
    """_destroy() does NOT remove keys from other namespaces."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    shared_map["panel_1-txt"] = Value("remove", read_only=True)
    shared_map["panel_2-txt"] = Value("keep", read_only=True)
    shared_map["panel_1_extra-txt"] = Value("keep too", read_only=True)

    inputs._destroy()

    assert "panel_1-txt" not in shared_map
    assert "panel_2-txt" in shared_map
    assert "panel_1_extra-txt" in shared_map


def test_inputs_destroy_calls_value_destroy():
    """_destroy() calls destroy() on each removed value."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    v = Value(42, read_only=True)
    shared_map["panel_1-txt"] = v

    inputs._destroy()

    assert v._destroyed is True
    with isolate():
        assert v.is_set() is False


def test_inputs_destroy_resurrection():
    """After _destroy(), new value for a removed key creates a fresh entry."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    old_value = Value("old", read_only=True)
    shared_map["panel_1-txt"] = old_value
    inputs._destroy()
    assert "panel_1-txt" not in shared_map

    # Old value is destroyed and raises on access
    with pytest.raises(DestroyedReactiveError):
        with isolate():
            old_value()

    # New value under the same key works normally
    new_value: Value[str] = Value(read_only=True)
    new_value._set("new")
    shared_map["panel_1-txt"] = new_value

    with isolate():
        assert shared_map["panel_1-txt"]() == "new"


@pytest.mark.asyncio
async def test_module_input_destroyed_on_session_destroy():
    """Module session destroy removes input from map; old reference raises."""
    root = _make_mock_root_session_non_stub()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    # Simulate an input value arriving from the client
    root.input._map["mod1-myobj"] = Value("hello", read_only=True)
    root.input._map["mod1-myobj"]._set("hello")

    # Grab a reference to the input Value before destroy
    with session_context(proxy):
        myobj = proxy.input["myobj"]

    with isolate():
        assert myobj() == "hello"

    # Destroy the module session
    await proxy.destroy()

    # The key is gone from the shared input map — a new module gets a fresh Value
    assert "mod1-myobj" not in root.input._map

    # The old reference is destroyed and raises on get()
    with pytest.raises(DestroyedReactiveError):
        with isolate():
            myobj()


def _make_mock_effect() -> Effect_:
    """Create a minimal mock that tracks destroy() calls."""

    class MockEffect:
        def __init__(self) -> None:
            self._destroyed = False

        def destroy(self) -> None:
            self._destroyed = True

    return cast(Effect_, MockEffect())


def _make_mock_renderer() -> Renderer[Any]:
    """Create a minimal mock renderer."""

    class MockRenderer:
        pass

    return cast(Renderer[Any], MockRenderer())


class _StubSession:
    """Minimal session stub for Outputs constructor."""

    def __init__(self) -> None:
        self.ns = ResolvedId("")

    def _is_hidden(self, name: str) -> bool:
        return False


def test_outputs_destroy_removes_namespaced_outputs():
    """_destroy() removes all outputs matching namespace prefix."""
    shared_outputs: dict[str, OutputInfo] = {}
    ns = ResolvedId("panel_1")
    stub = cast(Session, _StubSession())
    outputs = Outputs(stub, ns=ns, outputs=shared_outputs)

    effect1 = _make_mock_effect()
    effect2 = _make_mock_effect()
    effect3 = _make_mock_effect()
    shared_outputs["panel_1-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=effect1, suspend_when_hidden=True
    )
    shared_outputs["panel_1-table"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=effect2, suspend_when_hidden=True
    )
    shared_outputs["panel_2-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=effect3, suspend_when_hidden=True
    )

    outputs._destroy()

    assert "panel_1-plot" not in shared_outputs
    assert "panel_1-table" not in shared_outputs
    assert "panel_2-plot" in shared_outputs


def test_outputs_destroy_preserves_other_namespaces():
    """_destroy() does NOT remove outputs from other namespaces."""
    shared_outputs: dict[str, OutputInfo] = {}
    ns = ResolvedId("panel_1")
    stub = cast(Session, _StubSession())
    outputs = Outputs(stub, ns=ns, outputs=shared_outputs)

    effect1 = _make_mock_effect()
    effect2 = _make_mock_effect()
    shared_outputs["panel_1-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=effect1, suspend_when_hidden=True
    )
    shared_outputs["other-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=effect2, suspend_when_hidden=True
    )

    outputs._destroy()

    assert "panel_1-plot" not in shared_outputs
    assert "other-plot" in shared_outputs
    assert not cast(Any, effect2)._destroyed


def test_outputs_destroy_destroys_effects():
    """_destroy() calls destroy() on each removed output's effect."""
    shared_outputs: dict[str, OutputInfo] = {}
    ns = ResolvedId("panel_1")
    stub = cast(Session, _StubSession())
    outputs = Outputs(stub, ns=ns, outputs=shared_outputs)

    effect1 = _make_mock_effect()
    shared_outputs["panel_1-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=effect1, suspend_when_hidden=True
    )

    outputs._destroy()

    assert cast(Any, effect1)._destroyed is True


def _make_mock_root_session() -> Session:
    """Create a minimal mock root session for SessionProxy tests."""

    class MockApp:
        pass

    class MockOutboundQueues:
        pass

    class MockBookmark:
        def __init__(self) -> None:
            self._on_get_exclude: list[Any] = []

    class MockRootSession:
        def __init__(self) -> None:
            self.app = MockApp()
            self.id = "mock_session_id"
            self.ns = ResolvedId("")
            self.input = Inputs(values={}, ns=ResolvedId(""))
            self.output = Outputs(cast(Session, self), ns=ResolvedId(""), outputs={})
            self._outbound_message_queues = MockOutboundQueues()
            self._downloads: dict[str, Any] = {}
            self._message_handlers: dict[str, Any] = {}
            self._dynamic_routes: dict[str, Any] = {}
            self.bookmark = MockBookmark()
            self._destroy_callbacks_by_ns: dict[str, _utils.AsyncCallbacks] = {}

        def _is_hidden(self, name: str) -> bool:
            return False

        def is_stub_session(self) -> bool:
            return True

        def make_scope(self, id: str) -> SessionProxy:
            return SessionProxy(
                root_session=cast(Session, self), ns=ResolvedId(str(id))
            )

        def root_scope(self) -> MockRootSession:
            return self

    return cast(Session, MockRootSession())


@pytest.mark.asyncio
async def test_session_proxy_on_destroy_fires_callbacks():
    """on_destroy() registers callbacks that fire on destroy()."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    called: list[str] = []
    proxy.on_destroy(lambda: called.append("a"))  # pyright: ignore[reportArgumentType]
    proxy.on_destroy(lambda: called.append("b"))  # pyright: ignore[reportArgumentType]

    await proxy.destroy()

    assert called == ["a", "b"]


@pytest.mark.asyncio
async def test_session_proxy_destroy_is_idempotent():
    """Second destroy() call does nothing."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    call_count = 0

    def cb() -> None:
        nonlocal call_count
        call_count += 1

    proxy.on_destroy(cb)
    await proxy.destroy()
    assert call_count == 1

    await proxy.destroy()
    assert call_count == 1


@pytest.mark.asyncio
async def test_session_proxy_destroy_clears_callbacks():
    """Callbacks list is cleared after destroy (no reference retention)."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    proxy.on_destroy(lambda: None)

    await proxy.destroy()
    # Callbacks are removed from root session after destroy
    assert "mod1" not in cast(Any, root)._destroy_callbacks_by_ns


@pytest.mark.asyncio
async def test_session_proxy_namespace_reusable_after_destroy():
    """After destroy, a new proxy for the same namespace works normally."""
    root = _make_mock_root_session()
    proxy1 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    await proxy1.destroy()

    # A new proxy for the same namespace should work fine
    proxy2 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    # Can access input/output without error
    _ = proxy2.input
    _ = proxy2.output


@pytest.mark.asyncio
async def test_destroy_cleans_up_message_handlers():
    """destroy() removes namespaced message handlers from root session."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    # Simulate registering message handlers (normally done via set_message_handler)
    cast(Any, root)._message_handlers["mod1-custom_msg"] = lambda: None
    cast(Any, root)._message_handlers["mod1-another"] = lambda: None
    cast(Any, root)._message_handlers["other-msg"] = lambda: None

    await proxy.destroy()

    assert "mod1-custom_msg" not in cast(Any, root)._message_handlers
    assert "mod1-another" not in cast(Any, root)._message_handlers
    assert "other-msg" in cast(Any, root)._message_handlers


@pytest.mark.asyncio
async def test_destroy_cleans_up_dynamic_routes():
    """destroy() removes namespaced dynamic routes from root session."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    cast(Any, root)._dynamic_routes["mod1-upload"] = lambda: None
    cast(Any, root)._dynamic_routes["other-upload"] = lambda: None

    await proxy.destroy()

    assert "mod1-upload" not in cast(Any, root)._dynamic_routes
    assert "other-upload" in cast(Any, root)._dynamic_routes


@pytest.mark.asyncio
async def test_destroy_cleans_up_downloads():
    """destroy() removes namespaced download entries from root session."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    cast(Any, root)._downloads["mod1-report"] = "mock_download_info"
    cast(Any, root)._downloads["other-report"] = "mock_download_info"

    await proxy.destroy()

    assert "mod1-report" not in cast(Any, root)._downloads
    assert "other-report" in cast(Any, root)._downloads


@pytest.mark.asyncio
async def test_destroy_cleans_up_child_namespace_registrations():
    """destroy() removes child namespace entries from handlers/routes/downloads."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    # Parent and child namespace entries
    cast(Any, root)._message_handlers["mod1-msg"] = lambda: None
    cast(Any, root)._message_handlers["mod1-child-msg"] = lambda: None
    cast(Any, root)._dynamic_routes["mod1-route"] = lambda: None
    cast(Any, root)._dynamic_routes["mod1-child-route"] = lambda: None
    cast(Any, root)._downloads["mod1-dl"] = "info"
    cast(Any, root)._downloads["mod1-child-dl"] = "info"

    await proxy.destroy()

    # Both parent and child entries should be removed
    assert "mod1-msg" not in cast(Any, root)._message_handlers
    assert "mod1-child-msg" not in cast(Any, root)._message_handlers
    assert "mod1-route" not in cast(Any, root)._dynamic_routes
    assert "mod1-child-route" not in cast(Any, root)._dynamic_routes
    assert "mod1-dl" not in cast(Any, root)._downloads
    assert "mod1-child-dl" not in cast(Any, root)._downloads


def test_session_proxy_callbacks_stored_on_root():
    """Destroy callbacks are stored on the root session, not on the proxy."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    proxy.on_destroy(lambda: None)

    # Callbacks live on root, keyed by namespace
    assert "mod1" in cast(Any, root)._destroy_callbacks_by_ns
    assert not hasattr(proxy, "_on_destroy_callbacks_by_ns")


def _make_mock_root_session_non_stub() -> Session:
    """Mock root session where is_stub_session() returns False (for Effect_ tests)."""

    class MockApp:
        pass

    class MockOutboundQueues:
        pass

    class MockBookmark:
        def __init__(self) -> None:
            self._on_get_exclude: list[Any] = []

    class MockRootSession:
        def __init__(self) -> None:
            self.app = MockApp()
            self.id = "mock_session_id"
            self.ns = ResolvedId("")
            self.input = Inputs(values={}, ns=ResolvedId(""))
            self.output = Outputs(cast(Session, self), ns=ResolvedId(""), outputs={})
            self._outbound_message_queues = MockOutboundQueues()
            self._downloads: dict[str, Any] = {}
            self._message_handlers: dict[str, Any] = {}
            self._dynamic_routes: dict[str, Any] = {}
            self.bookmark = MockBookmark()
            self._destroy_callbacks_by_ns: dict[str, _utils.AsyncCallbacks] = {}

        def _is_hidden(self, name: str) -> bool:
            return False

        def is_stub_session(self) -> bool:
            return False

        def on_ended(self, fn: Any) -> None:
            pass  # No-op for testing

        def _increment_busy_count(self) -> None:
            pass

        def _decrement_busy_count(self) -> None:
            pass

        def make_scope(self, id: str) -> SessionProxy:
            return SessionProxy(
                root_session=cast(Session, self), ns=ResolvedId(str(id))
            )

        def root_scope(self) -> MockRootSession:
            return self

    return cast(Session, MockRootSession())


@pytest.mark.asyncio
async def test_value_self_registers_with_session_proxy():
    """Value created within SessionProxy context registers destroy."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    with session_context(proxy):
        v = Value(42)

    await proxy.destroy()
    with isolate():
        assert v.is_set() is False


@pytest.mark.asyncio
async def test_calc_self_registers_with_session_proxy():
    """Calc_ created within SessionProxy context registers destroy."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    with session_context(proxy):

        @calc()
        def doubled():
            return 42

    with isolate():
        assert doubled() == 42

    await proxy.destroy()

    with pytest.raises(DestroyedReactiveError):
        with isolate():
            doubled()


@pytest.mark.asyncio
async def test_effect_self_registers_with_session_proxy():
    """Effect_ created within SessionProxy context registers destroy."""
    root = _make_mock_root_session_non_stub()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    with session_context(proxy):

        @effect()
        def my_effect():
            pass

    await proxy.destroy()
    assert my_effect._destroyed is True


@pytest.mark.asyncio
async def test_invalidate_later_cancelled_on_destroy():
    """invalidate_later() timer is cancelled when its effect is destroyed via destroy."""
    root = _make_mock_root_session_non_stub()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    exec_count = 0

    with session_context(proxy):

        @effect()
        def ticking_effect():
            nonlocal exec_count
            # Schedule re-invalidation in 10 seconds (long enough to never fire in test)
            invalidate_later(10)
            exec_count += 1

    # Flush to run the effect once and start the invalidate_later timer
    await flush()
    assert exec_count == 1

    # Collect the asyncio tasks before destroy
    tasks_before = {t for t in asyncio.all_tasks() if not t.done()}

    # Destroy destroys the effect, which invalidates its context,
    # which cancels the invalidate_later task via ctx.on_invalidate
    await proxy.destroy()

    # Give the event loop a tick to process the cancellation
    await asyncio.sleep(0)

    # The invalidate_later task should now be done (cancelled)
    tasks_after = {t for t in asyncio.all_tasks() if not t.done()}
    cancelled_tasks = tasks_before - tasks_after
    assert len(cancelled_tasks) >= 1, "Expected at least one task to be cancelled"

    # Effect should not have run again
    assert exec_count == 1


def test_no_registration_without_session():
    """Reactive objects created without a session do NOT register destroy."""
    v = Value(42)
    # Value and Calc still have _destroyed for their own destroy logic
    assert v._destroyed is False

    @calc()
    def doubled():
        return v() * 2

    assert doubled._destroyed is False


@pytest.mark.asyncio
async def test_session_destroy_end_to_end():
    """session.destroy() destroys effects, calcs, values, and removes inputs/outputs."""
    root = _make_mock_root_session_non_stub()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("panel_1"))

    with session_context(proxy):
        # Create a reactive value
        counter = Value(0)

        # Create a calc
        @calc()
        def doubled():
            return counter() * 2

        # Force calc evaluation
        with isolate():
            assert doubled() == 0

        # Create an effect
        @effect()
        def my_effect():
            pass

    # Simulate inputs being populated by client
    root.input._map["panel_1-txt"] = Value("hello", read_only=True)
    root.input._map[".clientdata_output_panel_1-plot_hidden"] = Value(
        False, read_only=True
    )

    # Simulate output being registered
    mock_effect = _make_mock_effect()
    root.output._outputs["panel_1-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=mock_effect, suspend_when_hidden=True
    )

    # Destroy the module
    await proxy.destroy()

    # Value is destroyed
    with isolate():
        assert counter.is_set() is False

    # Calc raises DestroyedReactiveError
    with pytest.raises(DestroyedReactiveError):
        with isolate():
            doubled()

    # Effect is destroyed
    assert my_effect._destroyed is True

    # Input keys removed
    assert "panel_1-txt" not in root.input._map
    assert ".clientdata_output_panel_1-plot_hidden" not in root.input._map

    # Output removed and its effect destroyed
    assert "panel_1-plot" not in root.output._outputs
    assert cast(Any, mock_effect)._destroyed is True


@pytest.mark.asyncio
async def test_nested_module_destroy():
    """Parent destroy cleans up nested module inputs/outputs by prefix matching."""
    root = _make_mock_root_session()
    parent_proxy = SessionProxy(root_session=root, ns=ResolvedId("parent"))

    # Simulate nested module inputs (parent-child-input)
    root.input._map["parent-txt"] = Value("parent input", read_only=True)
    root.input._map["parent-child-txt"] = Value("child input", read_only=True)
    root.input._map["other-txt"] = Value("other input", read_only=True)

    # Simulate nested module outputs
    effect_parent = _make_mock_effect()
    effect_child = _make_mock_effect()
    effect_other = _make_mock_effect()
    root.output._outputs["parent-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=effect_parent, suspend_when_hidden=True
    )
    root.output._outputs["parent-child-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=effect_child, suspend_when_hidden=True
    )
    root.output._outputs["other-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=effect_other, suspend_when_hidden=True
    )

    await parent_proxy.destroy()

    # Parent and child inputs removed
    assert "parent-txt" not in root.input._map
    assert "parent-child-txt" not in root.input._map
    # Other namespace untouched
    assert "other-txt" in root.input._map

    # Parent and child outputs removed
    assert "parent-plot" not in root.output._outputs
    assert "parent-child-plot" not in root.output._outputs
    assert "other-plot" in root.output._outputs

    # Effects destroyed for parent and child, not other
    assert cast(Any, effect_parent)._destroyed is True
    assert cast(Any, effect_child)._destroyed is True
    assert not cast(Any, effect_other)._destroyed


# ---------------------------------------------------------------------------
# ExpressStubSession destroy tests
# ---------------------------------------------------------------------------
def test_express_stub_session_on_destroy_is_noop():
    """ExpressStubSession.on_destroy() silently does nothing."""
    stub = ExpressStubSession()

    called: list[str] = []
    # Should not raise, should not store anything
    stub.on_destroy(lambda: called.append("x"))  # pyright: ignore[reportArgumentType]
    assert called == []


@pytest.mark.asyncio
async def test_express_stub_session_destroy_is_noop():
    """ExpressStubSession.destroy() silently does nothing."""
    stub = ExpressStubSession()
    # Should not raise
    await stub.destroy()


def test_express_stub_session_has_no_destroy_state():
    """ExpressStubSession does not have _destroy_callbacks_by_ns."""
    stub = ExpressStubSession()
    assert not hasattr(stub, "_destroy_callbacks_by_ns")


@pytest.mark.asyncio
async def test_express_stub_session_proxy_destroy_is_silent():
    """SessionProxy created from ExpressStubSession silently does nothing on destroy."""
    stub = ExpressStubSession()
    proxy = stub.make_scope("mod1")
    assert isinstance(proxy, SessionProxy)

    proxy.on_destroy(lambda: None)
    # destroy should not raise
    await proxy.destroy()


# ---------------------------------------------------------------------------
# AppSession destroy tests
# ---------------------------------------------------------------------------
def test_app_session_has_destroy_methods():
    """AppSession has on_destroy() and destroy() methods."""
    assert hasattr(AppSession, "on_destroy")
    assert hasattr(AppSession, "destroy")


# ---------------------------------------------------------------------------
# SessionProxy async callback tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_session_proxy_on_destroy_accepts_async_callback():
    """on_destroy() accepts async callbacks and awaits them on destroy."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    called: list[str] = []

    async def async_cb() -> None:
        called.append("async")

    proxy.on_destroy(async_cb)
    await proxy.destroy()

    assert called == ["async"]


@pytest.mark.asyncio
async def test_session_proxy_on_destroy_mixed_sync_async():
    """on_destroy() handles a mix of sync and async callbacks."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    called: list[str] = []

    def sync_cb() -> None:
        called.append("sync")

    async def async_cb() -> None:
        called.append("async")

    proxy.on_destroy(sync_cb)
    proxy.on_destroy(async_cb)
    proxy.on_destroy(lambda: None)  # no-op sync

    await proxy.destroy()

    assert called == ["sync", "async"]


@pytest.mark.asyncio
async def test_session_proxy_on_destroy_after_destroy():
    """Registering a callback after destroy creates a fresh callback set for the namespace."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    await proxy.destroy()

    called: list[str] = []
    # Register after destroy — goes into a new AsyncCallbacks for this namespace
    proxy.on_destroy(
        lambda: called.append("late")
    )  # pyright: ignore[reportArgumentType]
    assert called == []

    # A second destroy fires the newly registered callback
    await proxy.destroy()
    assert called == ["late"]


@pytest.mark.asyncio
async def test_session_proxy_multiple_proxies_same_namespace():
    """Multiple proxies for the same namespace share destroy state."""
    root = _make_mock_root_session()
    proxy1 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    proxy2 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    called: list[str] = []
    proxy1.on_destroy(
        lambda: called.append("from_p1")
    )  # pyright: ignore[reportArgumentType]
    proxy2.on_destroy(
        lambda: called.append("from_p2")
    )  # pyright: ignore[reportArgumentType]

    # Destroy via proxy1 should fire all callbacks for the namespace
    await proxy1.destroy()

    assert "from_p1" in called
    assert "from_p2" in called


@pytest.mark.asyncio
async def test_session_proxy_different_namespaces_independent():
    """Destroying one namespace does not affect another."""
    root = _make_mock_root_session()
    proxy_a = SessionProxy(root_session=root, ns=ResolvedId("mod_a"))
    proxy_b = SessionProxy(root_session=root, ns=ResolvedId("mod_b"))

    called_a: list[str] = []
    called_b: list[str] = []
    proxy_a.on_destroy(
        lambda: called_a.append("a")
    )  # pyright: ignore[reportArgumentType]
    proxy_b.on_destroy(
        lambda: called_b.append("b")
    )  # pyright: ignore[reportArgumentType]

    await proxy_a.destroy()

    assert called_a == ["a"]
    assert called_b == []


# ---------------------------------------------------------------------------
# Module re-creation after destroy
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_module_recreated_after_destroy():
    """A module can be fully re-created under the same namespace after destroy."""
    root = _make_mock_root_session()

    # First lifecycle
    proxy1 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    called_1: list[str] = []
    proxy1.on_destroy(
        lambda: called_1.append("cleanup1")
    )  # pyright: ignore[reportArgumentType]
    await proxy1.destroy()
    assert called_1 == ["cleanup1"]

    # Second lifecycle — same namespace
    proxy2 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    _ = proxy2.input
    _ = proxy2.output

    # New callbacks can be registered and fire independently
    called_2: list[str] = []
    proxy2.on_destroy(
        lambda: called_2.append("cleanup2")
    )  # pyright: ignore[reportArgumentType]
    await proxy2.destroy()

    assert called_2 == ["cleanup2"]
    # First lifecycle's callback was not re-invoked
    assert called_1 == ["cleanup1"]


@pytest.mark.asyncio
async def test_module_recreated_with_new_inputs_outputs():
    """Re-created module gets fresh inputs/outputs after destroy cleaned the old ones."""
    root = _make_mock_root_session()

    # First lifecycle — populate inputs and outputs
    proxy1 = SessionProxy(root_session=root, ns=ResolvedId("panel_1"))
    root.input._map["panel_1-txt"] = Value("old value", read_only=True)
    root.output._outputs["panel_1-plot"] = OutputInfo(
        renderer=_make_mock_renderer(),
        effect=_make_mock_effect(),
        suspend_when_hidden=True,
    )

    await proxy1.destroy()

    # Old inputs/outputs are cleaned up
    assert "panel_1-txt" not in root.input._map
    assert "panel_1-plot" not in root.output._outputs

    # Second lifecycle — re-create under same namespace
    proxy2 = SessionProxy(root_session=root, ns=ResolvedId("panel_1"))

    # New inputs and outputs can be populated
    root.input._map["panel_1-txt"] = Value("new value", read_only=True)
    root.output._outputs["panel_1-plot"] = OutputInfo(
        renderer=_make_mock_renderer(),
        effect=_make_mock_effect(),
        suspend_when_hidden=True,
    )

    with isolate():
        assert root.input._map["panel_1-txt"]() == "new value"
    assert "panel_1-plot" in root.output._outputs

    # Second destroy cleans up the new state
    await proxy2.destroy()
    assert "panel_1-txt" not in root.input._map
    assert "panel_1-plot" not in root.output._outputs


@pytest.mark.asyncio
async def test_module_recreated_with_reactive_objects():
    """Re-created module can register new reactive objects that tear down independently."""
    root = _make_mock_root_session_non_stub()

    # First lifecycle
    proxy1 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    with session_context(proxy1):
        v1 = Value(10)

    await proxy1.destroy()
    with isolate():
        assert v1.is_set() is False

    # Second lifecycle — new Value under same namespace
    proxy2 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    with session_context(proxy2):
        v2 = Value(20)

    with isolate():
        assert v2() == 20

    await proxy2.destroy()
    with isolate():
        assert v2.is_set() is False


# ---------------------------------------------------------------------------
# Descendant destroy ordering tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_destroy_cascades_to_child_namespaces():
    """Parent destroy fires callbacks for child namespaces too."""
    root = _make_mock_root_session()
    parent = SessionProxy(root_session=root, ns=ResolvedId("parent"))
    child = SessionProxy(root_session=root, ns=ResolvedId("parent-child"))

    called: list[str] = []
    parent.on_destroy(
        lambda: called.append("parent")
    )  # pyright: ignore[reportArgumentType]
    child.on_destroy(
        lambda: called.append("child")
    )  # pyright: ignore[reportArgumentType]

    await parent.destroy()

    assert "parent" in called
    assert "child" in called


@pytest.mark.asyncio
async def test_destroy_cascades_to_grandchild_namespaces():
    """Parent destroy fires callbacks for grandchild namespaces."""
    root = _make_mock_root_session()
    parent = SessionProxy(root_session=root, ns=ResolvedId("p"))
    child = SessionProxy(root_session=root, ns=ResolvedId("p-c"))
    grandchild = SessionProxy(root_session=root, ns=ResolvedId("p-c-gc"))

    called: list[str] = []
    parent.on_destroy(
        lambda: called.append("parent")
    )  # pyright: ignore[reportArgumentType]
    child.on_destroy(
        lambda: called.append("child")
    )  # pyright: ignore[reportArgumentType]
    grandchild.on_destroy(
        lambda: called.append("grandchild")
    )  # pyright: ignore[reportArgumentType]

    await parent.destroy()

    assert called == ["grandchild", "child", "parent"]


@pytest.mark.asyncio
async def test_destroy_children_before_parents():
    """Deepest namespaces are destroyed first (depth-first / reverse construction order)."""
    root = _make_mock_root_session()

    # Register callbacks at various nesting depths
    namespaces = ["a", "a-b", "a-b-c", "a-b-c-d", "a-x"]
    for ns in namespaces:
        proxy = SessionProxy(root_session=root, ns=ResolvedId(ns))
        # Capture ns in default arg to avoid closure issues
        proxy.on_destroy(
            lambda n=ns: order.append(n)
        )  # pyright: ignore[reportArgumentType]

    order: list[str] = []
    top = SessionProxy(root_session=root, ns=ResolvedId("a"))
    await top.destroy()

    # Most nested should come first; within the same depth, order is not
    # guaranteed by the spec, but deepest must precede their ancestors.
    for i, ns in enumerate(order):
        depth = ns.count("-")
        for later_ns in order[i + 1 :]:
            later_depth = later_ns.count("-")
            # A deeper namespace must not appear after a shallower one
            # (unless they are at the same depth)
            assert later_depth <= depth, (
                f"'{later_ns}' (depth {later_depth}) appeared after "
                f"'{ns}' (depth {depth}) — children must be destroyed before parents"
            )


@pytest.mark.asyncio
async def test_destroy_does_not_cascade_to_sibling_namespaces():
    """Tearing down 'a' does not affect 'b' even if 'b' has children."""
    root = _make_mock_root_session()
    proxy_a = SessionProxy(root_session=root, ns=ResolvedId("a"))
    proxy_b = SessionProxy(root_session=root, ns=ResolvedId("b"))
    proxy_b_child = SessionProxy(root_session=root, ns=ResolvedId("b-child"))

    called: list[str] = []
    proxy_a.on_destroy(
        lambda: called.append("a")
    )  # pyright: ignore[reportArgumentType]
    proxy_b.on_destroy(
        lambda: called.append("b")
    )  # pyright: ignore[reportArgumentType]
    proxy_b_child.on_destroy(
        lambda: called.append("b-child")
    )  # pyright: ignore[reportArgumentType]

    await proxy_a.destroy()

    assert called == ["a"]
    # b and b-child callbacks still registered
    assert "b" in cast(Any, root)._destroy_callbacks_by_ns
    assert "b-child" in cast(Any, root)._destroy_callbacks_by_ns


@pytest.mark.asyncio
async def test_child_destroy_does_not_cascade_to_parent():
    """Tearing down a child does not fire parent callbacks."""
    root = _make_mock_root_session()
    parent = SessionProxy(root_session=root, ns=ResolvedId("parent"))
    child = SessionProxy(root_session=root, ns=ResolvedId("parent-child"))

    called: list[str] = []
    parent.on_destroy(
        lambda: called.append("parent")
    )  # pyright: ignore[reportArgumentType]
    child.on_destroy(
        lambda: called.append("child")
    )  # pyright: ignore[reportArgumentType]

    await child.destroy()

    assert called == ["child"]
    # Parent callbacks still registered
    assert "parent" in cast(Any, root)._destroy_callbacks_by_ns


# ---------------------------------------------------------------------------
# Input/output destroy ordering tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_inputs_available_during_destroy_callbacks():
    """Input values can still be read inside destroy callbacks."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    # Populate an input
    root.input._map["mod1-txt"] = Value("hello", read_only=True)

    observed_value: list[str | None] = []

    def read_input() -> None:
        v = root.input._map.get("mod1-txt")
        if v is not None:
            with isolate():
                observed_value.append(v())
        else:
            observed_value.append(None)

    proxy.on_destroy(read_input)
    await proxy.destroy()

    # The callback should have been able to read the input value
    assert observed_value == ["hello"]
    # After destroy completes, the input is removed
    assert "mod1-txt" not in root.input._map


@pytest.mark.asyncio
async def test_outputs_available_during_destroy_callbacks():
    """Output entries still exist during destroy callbacks."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    mock_effect = _make_mock_effect()
    root.output._outputs["mod1-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=mock_effect, suspend_when_hidden=True
    )

    output_existed: list[bool] = []

    def check_output() -> None:
        output_existed.append("mod1-plot" in root.output._outputs)

    proxy.on_destroy(check_output)
    await proxy.destroy()

    # Output was still present when the callback ran
    assert output_existed == [True]
    # After destroy completes, the output is removed
    assert "mod1-plot" not in root.output._outputs


# ---------------------------------------------------------------------------
# Data persistence pattern tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_caller_owned_value_survives_destroy():
    """A reactive value created outside the module survives module destroy.

    This is the recommended pattern for persisting data after destroy:
    create the value in the caller's scope and pass it into the module.
    """
    root = _make_mock_root_session()

    # Caller creates and owns the value (outside any module)
    saved_data: Value[str | None] = Value(None)

    # Module sets the caller-owned value
    proxy = SessionProxy(root_session=root, ns=ResolvedId("editor"))
    with session_context(proxy):
        # Simulate module writing to the passed-in value
        saved_data.set("user input")

    with isolate():
        assert saved_data() == "user input"

    # Destroy the module
    await proxy.destroy()

    # The caller-owned value is still valid and readable
    with isolate():
        assert saved_data() == "user input"
        assert saved_data.is_set() is True


@pytest.mark.asyncio
async def test_module_owned_value_destroyed_on_destroy():
    """A reactive value created inside the module is destroyed on destroy.

    This demonstrates why returning a reactive value from a module is
    problematic — the value becomes invalid after destroy.
    """
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("editor"))

    with session_context(proxy):
        # Module creates its own value (bad pattern for persistence)
        module_data = Value("important data")

    with isolate():
        assert module_data() == "important data"

    # Destroy the module
    await proxy.destroy()

    with isolate():
        assert module_data.is_set() is False


# ---------------------------------------------------------------------------
# Garbage collection tests — session should not pin reactive objects
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_value_gc_after_session_registration():
    """Value is garbage collected when unreachable, despite on_destroy registration."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("gc_test"))

    with session_context(proxy):
        v = Value(42)
    ref = weakref.ref(v)
    del v
    gc.collect()
    assert (
        ref() is None
    ), "Session should not prevent Value from being garbage collected"


@pytest.mark.asyncio
async def test_calc_gc_after_session_registration():
    """Calc is garbage collected when unreachable, despite on_destroy registration."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("gc_test"))

    with session_context(proxy):

        @calc
        def my_calc():
            return 42

    ref = weakref.ref(my_calc)
    del my_calc
    gc.collect()
    assert ref() is None, "Session should not prevent Calc from being garbage collected"


@pytest.mark.asyncio
async def test_effect_gc_after_session_registration():
    """Effect is garbage collected when unreachable, despite on_destroy registration."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("gc_test"))

    with session_context(proxy):
        eff = Effect_(lambda: None, suspended=True)
    ref = weakref.ref(eff)
    del eff
    gc.collect()
    assert (
        ref() is None
    ), "Session should not prevent Effect from being garbage collected"


@pytest.mark.asyncio
async def test_dead_destroy_callbacks_silently_skipped():
    """Destroy callbacks for GC'd objects are silently skipped."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("gc_test"))

    with session_context(proxy):
        v = Value(42)
    del v
    gc.collect()

    # Invoking destroy on the proxy should not raise, even though the Value's
    # weak callback is now dead.
    await proxy.destroy()
