"""Tests for reactive teardown behavior."""

from __future__ import annotations

from typing import Any, cast

import pytest

from shiny import _utils
from shiny._namespaces import ResolvedId
from shiny.reactive import DestroyedReactiveError, Value, calc, effect, flush, isolate
from shiny.reactive._reactives import Effect_
from shiny.render.renderer import Renderer
from shiny.session._session import Inputs, OutputInfo, Outputs, Session, SessionProxy
from shiny.session._utils import session_context


def test_destroyed_reactive_error_is_exception():
    assert issubclass(DestroyedReactiveError, Exception)
    err = DestroyedReactiveError("test message")
    assert str(err) == "test message"


@pytest.mark.asyncio
async def test_value_teardown_unsets_value():
    """After _teardown(), value is unset."""
    v = Value(42)
    with isolate():
        assert v.is_set() is True
    v._teardown()
    with isolate():
        assert v.is_set() is False


@pytest.mark.asyncio
async def test_value_teardown_invalidates_value_dependents():
    """_teardown() invalidates downstream value dependents."""
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

    v._teardown()
    await flush()
    assert call_count == 2


@pytest.mark.asyncio
async def test_value_teardown_invalidates_is_set_dependents():
    """_teardown() invalidates is_set() dependents."""
    v = Value(10)
    is_set_results: list[bool] = []

    @effect()
    def _():
        is_set_results.append(v.is_set())

    await flush()
    assert is_set_results == [True]

    v._teardown()
    await flush()
    assert is_set_results == [True, False]


@pytest.mark.asyncio
async def test_value_teardown_is_idempotent():
    """Second _teardown() call is a no-op."""
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

    v._teardown()
    await flush()
    assert call_count == 2

    # Second teardown should NOT invalidate again
    v._teardown()
    await flush()
    assert call_count == 2


@pytest.mark.asyncio
async def test_value_teardown_works_on_read_only():
    """_teardown() works on read-only values (input values)."""
    v = Value(42, read_only=True)
    with isolate():
        assert v.is_set() is True
    v._teardown()
    with isolate():
        assert v.is_set() is False


@pytest.mark.asyncio
async def test_calc_teardown_raises_on_subsequent_call():
    """After _teardown(), calling the calc raises DestroyedReactiveError."""
    v = Value(10)

    @calc()
    def doubled():
        return v() * 2

    with isolate():
        assert doubled() == 20

    doubled._teardown()

    with pytest.raises(DestroyedReactiveError, match="has been destroyed"):
        doubled()


@pytest.mark.asyncio
async def test_calc_teardown_invalidates_context():
    """_teardown() invalidates the calc's current context (breaks upstream)."""
    v = Value(10)

    @calc()
    def doubled():
        return v() * 2

    # Force evaluation to create the context
    with isolate():
        assert doubled() == 20

    # After teardown, changing v should NOT cause calc to re-register
    doubled._teardown()
    v.set(20)
    await flush()


@pytest.mark.asyncio
async def test_calc_teardown_invalidates_downstream_dependents():
    """_teardown() invalidates downstream dependents of the calc."""
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

    doubled._teardown()
    await flush()
    assert results == [20, "destroyed"]


@pytest.mark.asyncio
async def test_calc_teardown_is_idempotent():
    """Second _teardown() call is a no-op."""
    v = Value(10)

    @calc()
    def doubled():
        return v() * 2

    with isolate():
        assert doubled() == 20

    doubled._teardown()
    doubled._teardown()  # Should not raise

    with pytest.raises(DestroyedReactiveError):
        doubled()


@pytest.mark.asyncio
async def test_calc_async_teardown():
    """Async calc teardown behaves the same as sync."""
    v = Value(10)

    @calc()
    async def doubled():
        return v() * 2

    with isolate():
        result = await doubled()
    assert result == 20

    doubled._teardown()

    with pytest.raises(DestroyedReactiveError, match="has been destroyed"):
        await doubled()


def test_inputs_teardown_removes_namespaced_keys():
    """_teardown() removes all keys matching the namespace prefix."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    shared_map["panel_1-txt"] = Value("hello", read_only=True)
    shared_map["panel_1-slider"] = Value(5, read_only=True)
    shared_map["other-txt"] = Value("keep", read_only=True)

    inputs._teardown()

    assert "panel_1-txt" not in shared_map
    assert "panel_1-slider" not in shared_map
    assert "other-txt" in shared_map


def test_inputs_teardown_removes_clientdata_keys():
    """_teardown() removes per-output clientdata keys matching the namespace."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    shared_map[".clientdata_output_panel_1-my_plot_hidden"] = Value(
        False, read_only=True
    )
    shared_map[".clientdata_output_panel_1-my_plot_width"] = Value(800, read_only=True)
    shared_map[".clientdata_output_panel_1-my_plot_height"] = Value(600, read_only=True)

    inputs._teardown()

    assert ".clientdata_output_panel_1-my_plot_hidden" not in shared_map
    assert ".clientdata_output_panel_1-my_plot_width" not in shared_map
    assert ".clientdata_output_panel_1-my_plot_height" not in shared_map


def test_inputs_teardown_preserves_global_clientdata():
    """_teardown() does NOT remove global clientdata keys."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    shared_map[".clientdata_pixelratio"] = Value(2.0, read_only=True)
    shared_map[".clientdata_url_protocol"] = Value("https:", read_only=True)
    shared_map[".clientdata_singletons"] = Value("", read_only=True)
    shared_map["panel_1-txt"] = Value("remove me", read_only=True)

    inputs._teardown()

    assert ".clientdata_pixelratio" in shared_map
    assert ".clientdata_url_protocol" in shared_map
    assert ".clientdata_singletons" in shared_map
    assert "panel_1-txt" not in shared_map


def test_inputs_teardown_preserves_other_namespaces():
    """_teardown() does NOT remove keys from other namespaces."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    shared_map["panel_1-txt"] = Value("remove", read_only=True)
    shared_map["panel_2-txt"] = Value("keep", read_only=True)
    shared_map["panel_1_extra-txt"] = Value("keep too", read_only=True)

    inputs._teardown()

    assert "panel_1-txt" not in shared_map
    assert "panel_2-txt" in shared_map
    assert "panel_1_extra-txt" in shared_map


def test_inputs_teardown_calls_value_teardown():
    """_teardown() calls _teardown() on each removed value."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    v = Value(42, read_only=True)
    shared_map["panel_1-txt"] = v

    inputs._teardown()

    assert v._torn_down is True
    with isolate():
        assert v.is_set() is False


def test_inputs_teardown_resurrection():
    """After teardown, new value for a removed key creates a fresh entry."""
    shared_map: dict[str, Value[Any]] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    shared_map["panel_1-txt"] = Value("old", read_only=True)
    inputs._teardown()
    assert "panel_1-txt" not in shared_map

    new_value: Value[str] = Value(read_only=True)
    new_value._set("new")
    shared_map["panel_1-txt"] = new_value

    with isolate():
        assert shared_map["panel_1-txt"]() == "new"


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


def test_outputs_teardown_removes_namespaced_outputs():
    """_teardown() removes all outputs matching namespace prefix."""
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

    outputs._teardown()

    assert "panel_1-plot" not in shared_outputs
    assert "panel_1-table" not in shared_outputs
    assert "panel_2-plot" in shared_outputs


def test_outputs_teardown_preserves_other_namespaces():
    """_teardown() does NOT remove outputs from other namespaces."""
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

    outputs._teardown()

    assert "panel_1-plot" not in shared_outputs
    assert "other-plot" in shared_outputs
    assert not cast(Any, effect2)._destroyed


def test_outputs_teardown_destroys_effects():
    """_teardown() calls destroy() on each removed output's effect."""
    shared_outputs: dict[str, OutputInfo] = {}
    ns = ResolvedId("panel_1")
    stub = cast(Session, _StubSession())
    outputs = Outputs(stub, ns=ns, outputs=shared_outputs)

    effect1 = _make_mock_effect()
    shared_outputs["panel_1-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=effect1, suspend_when_hidden=True
    )

    outputs._teardown()

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
            self.bookmark = MockBookmark()
            self._teardown_callbacks: dict[str, _utils.AsyncCallbacks] = {}
            self._torn_down_scopes: set[str] = set()

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
async def test_session_proxy_on_teardown_fires_callbacks():
    """on_teardown() registers callbacks that fire on teardown()."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    called: list[str] = []
    proxy.on_teardown(lambda: called.append("a"))  # pyright: ignore[reportArgumentType]
    proxy.on_teardown(lambda: called.append("b"))  # pyright: ignore[reportArgumentType]

    await proxy.teardown()

    assert called == ["a", "b"]


@pytest.mark.asyncio
async def test_session_proxy_teardown_is_idempotent():
    """Second teardown() call does nothing."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    call_count = 0

    def cb() -> None:
        nonlocal call_count
        call_count += 1

    proxy.on_teardown(cb)
    await proxy.teardown()
    assert call_count == 1

    await proxy.teardown()
    assert call_count == 1


@pytest.mark.asyncio
async def test_session_proxy_teardown_clears_callbacks():
    """Callbacks list is cleared after teardown (no reference retention)."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    proxy.on_teardown(lambda: None)

    await proxy.teardown()
    # Callbacks are removed from root session after teardown
    assert "mod1" not in root._teardown_callbacks


@pytest.mark.asyncio
async def test_session_proxy_teardown_visible_from_new_proxy():
    """A new proxy for the same namespace sees the torn-down state."""
    root = _make_mock_root_session()
    proxy1 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    await proxy1.teardown()

    proxy2 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    assert proxy2._torn_down is True

    with pytest.raises(RuntimeError, match="torn down"):
        _ = proxy2.input


def test_session_proxy_callbacks_stored_on_root():
    """Teardown callbacks are stored on the root session, not on the proxy."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    proxy.on_teardown(lambda: None)

    # Callbacks live on root, keyed by namespace
    assert "mod1" in root._teardown_callbacks
    assert not hasattr(proxy, "_on_teardown_callbacks")


@pytest.mark.asyncio
async def test_session_proxy_teardown_guards_input():
    """After teardown, accessing session.input raises RuntimeError."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    await proxy.teardown()

    with pytest.raises(RuntimeError, match="torn down"):
        _ = proxy.input


@pytest.mark.asyncio
async def test_session_proxy_teardown_guards_output():
    """After teardown, accessing session.output raises RuntimeError."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    await proxy.teardown()

    with pytest.raises(RuntimeError, match="torn down"):
        _ = proxy.output


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
            self.bookmark = MockBookmark()
            self._teardown_callbacks: dict[str, _utils.AsyncCallbacks] = {}
            self._torn_down_scopes: set[str] = set()

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
    """Value created within SessionProxy context registers _teardown."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    with session_context(proxy):
        v = Value(42)

    await proxy.teardown()
    with isolate():
        assert v.is_set() is False


@pytest.mark.asyncio
async def test_calc_self_registers_with_session_proxy():
    """Calc_ created within SessionProxy context registers _teardown."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    with session_context(proxy):

        @calc()
        def doubled():
            return 42

    from shiny.reactive import isolate

    with isolate():
        assert doubled() == 42

    await proxy.teardown()

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

    await proxy.teardown()
    assert my_effect._destroyed is True


def test_no_registration_without_session_proxy():
    """Reactive objects created without SessionProxy do NOT register teardown."""
    v = Value(42)
    assert v._torn_down is False

    @calc()
    def doubled():
        return v() * 2

    assert doubled._torn_down is False


@pytest.mark.asyncio
async def test_session_teardown_end_to_end():
    """session.teardown() destroys effects, tears down calcs, unsets values, removes inputs/outputs."""
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

    # Teardown the module
    await proxy.teardown()

    # Value is unset
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
async def test_nested_module_teardown():
    """Parent teardown cleans up nested module inputs/outputs by prefix matching."""
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

    await parent_proxy.teardown()

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
# ExpressStubSession teardown tests
# ---------------------------------------------------------------------------
def test_express_stub_session_on_teardown_is_noop():
    """ExpressStubSession.on_teardown() silently does nothing."""
    from shiny.express._stub_session import ExpressStubSession

    stub = ExpressStubSession()

    called: list[str] = []
    # Should not raise, should not store anything
    stub.on_teardown(lambda: called.append("x"))  # pyright: ignore[reportArgumentType]
    assert called == []


@pytest.mark.asyncio
async def test_express_stub_session_teardown_is_noop():
    """ExpressStubSession.teardown() silently does nothing."""
    from shiny.express._stub_session import ExpressStubSession

    stub = ExpressStubSession()
    # Should not raise
    await stub.teardown()


def test_express_stub_session_has_no_teardown_state():
    """ExpressStubSession does not have _teardown_callbacks or _torn_down_scopes."""
    from shiny.express._stub_session import ExpressStubSession

    stub = ExpressStubSession()
    assert not hasattr(stub, "_teardown_callbacks")
    assert not hasattr(stub, "_torn_down_scopes")


@pytest.mark.asyncio
async def test_express_stub_session_proxy_teardown_is_silent():
    """SessionProxy created from ExpressStubSession silently does nothing on teardown."""
    from shiny.express._stub_session import ExpressStubSession

    stub = ExpressStubSession()
    proxy = stub.make_scope("mod1")
    assert isinstance(proxy, SessionProxy)

    # on_teardown should not raise even though root has no _teardown_callbacks
    proxy.on_teardown(lambda: None)
    # teardown should not raise
    await proxy.teardown()


# ---------------------------------------------------------------------------
# AppSession teardown guard tests
# ---------------------------------------------------------------------------
def test_app_session_has_teardown_methods():
    """AppSession has on_teardown() and teardown() methods."""
    from shiny.session._session import AppSession

    assert hasattr(AppSession, "on_teardown")
    assert hasattr(AppSession, "teardown")


def _make_app_session_like_mock() -> Any:
    """Create a mock that behaves like AppSession for teardown testing.

    We can't easily instantiate a real AppSession (requires Connection, App),
    so we call the unbound methods directly.
    """
    from shiny.session._session import AppSession

    return AppSession


def test_app_session_on_teardown_raises_runtime_error():
    """AppSession.on_teardown() raises RuntimeError with descriptive message."""
    from shiny.session._session import AppSession

    # Call the unbound method with a dummy self
    with pytest.raises(RuntimeError, match="only supported on SessionProxy"):
        AppSession.on_teardown(cast(Any, None), lambda: None)


@pytest.mark.asyncio
async def test_app_session_teardown_raises_runtime_error():
    """AppSession.teardown() raises RuntimeError with descriptive message."""
    from shiny.session._session import AppSession

    with pytest.raises(RuntimeError, match="only supported on SessionProxy"):
        await AppSession.teardown(cast(Any, None))


# ---------------------------------------------------------------------------
# SessionProxy async callback tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_session_proxy_on_teardown_accepts_async_callback():
    """on_teardown() accepts async callbacks and awaits them on teardown."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    called: list[str] = []

    async def async_cb() -> None:
        called.append("async")

    proxy.on_teardown(async_cb)
    await proxy.teardown()

    assert called == ["async"]


@pytest.mark.asyncio
async def test_session_proxy_on_teardown_mixed_sync_async():
    """on_teardown() handles a mix of sync and async callbacks."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    called: list[str] = []

    def sync_cb() -> None:
        called.append("sync")

    async def async_cb() -> None:
        called.append("async")

    proxy.on_teardown(sync_cb)
    proxy.on_teardown(async_cb)
    proxy.on_teardown(lambda: None)  # no-op sync

    await proxy.teardown()

    assert called == ["sync", "async"]


@pytest.mark.asyncio
async def test_session_proxy_on_teardown_after_teardown_is_noop():
    """Registering a callback after teardown does not fire it."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    await proxy.teardown()

    called: list[str] = []
    # Register after teardown — callback should not fire
    proxy.on_teardown(
        lambda: called.append("late")
    )  # pyright: ignore[reportArgumentType]
    assert called == []

    # Second teardown should also be a no-op
    await proxy.teardown()
    assert called == []


@pytest.mark.asyncio
async def test_session_proxy_teardown_marks_scope_before_invoking_callbacks():
    """The scope is marked as torn down before callbacks run."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    torn_down_during_callback: list[bool] = []

    def check_state() -> None:
        torn_down_during_callback.append(proxy._torn_down)

    proxy.on_teardown(check_state)
    await proxy.teardown()

    assert torn_down_during_callback == [True]


@pytest.mark.asyncio
async def test_session_proxy_multiple_proxies_same_namespace():
    """Multiple proxies for the same namespace share teardown state."""
    root = _make_mock_root_session()
    proxy1 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    proxy2 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    called: list[str] = []
    proxy1.on_teardown(
        lambda: called.append("from_p1")
    )  # pyright: ignore[reportArgumentType]
    proxy2.on_teardown(
        lambda: called.append("from_p2")
    )  # pyright: ignore[reportArgumentType]

    # Teardown via proxy1 should fire all callbacks for the namespace
    await proxy1.teardown()

    assert "from_p1" in called
    assert "from_p2" in called

    # proxy2 should also see it as torn down
    assert proxy2._torn_down is True


@pytest.mark.asyncio
async def test_session_proxy_different_namespaces_independent():
    """Tearing down one namespace does not affect another."""
    root = _make_mock_root_session()
    proxy_a = SessionProxy(root_session=root, ns=ResolvedId("mod_a"))
    proxy_b = SessionProxy(root_session=root, ns=ResolvedId("mod_b"))

    called_a: list[str] = []
    called_b: list[str] = []
    proxy_a.on_teardown(
        lambda: called_a.append("a")
    )  # pyright: ignore[reportArgumentType]
    proxy_b.on_teardown(
        lambda: called_b.append("b")
    )  # pyright: ignore[reportArgumentType]

    await proxy_a.teardown()

    assert called_a == ["a"]
    assert called_b == []
    assert proxy_a._torn_down is True
    assert proxy_b._torn_down is False

    # proxy_b still works
    _ = proxy_b.input
    _ = proxy_b.output
