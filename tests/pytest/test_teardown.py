"""Tests for reactive teardown behavior."""

from __future__ import annotations

from typing import Any, cast

import pytest

from shiny import _utils
from shiny._namespaces import ResolvedId
from shiny.reactive import Value, calc, effect, flush, isolate
from shiny.reactive._reactives import DestroyedReactiveError, Effect_
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
            self._teardown_callbacks_by_ns: dict[str, _utils.AsyncCallbacks] = {}

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
    assert "mod1" not in cast(Any, root)._teardown_callbacks_by_ns


@pytest.mark.asyncio
async def test_session_proxy_namespace_reusable_after_teardown():
    """After teardown, a new proxy for the same namespace works normally."""
    root = _make_mock_root_session()
    proxy1 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    await proxy1.teardown()

    # A new proxy for the same namespace should work fine
    proxy2 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    # Can access input/output without error
    _ = proxy2.input
    _ = proxy2.output


def test_session_proxy_callbacks_stored_on_root():
    """Teardown callbacks are stored on the root session, not on the proxy."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    proxy.on_teardown(lambda: None)

    # Callbacks live on root, keyed by namespace
    assert "mod1" in cast(Any, root)._teardown_callbacks_by_ns
    assert not hasattr(proxy, "_on_teardown_callbacks_by_ns")


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
            self._teardown_callbacks_by_ns: dict[str, _utils.AsyncCallbacks] = {}

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


@pytest.mark.asyncio
async def test_invalidate_later_cancelled_on_teardown():
    """invalidate_later() timer is cancelled when its effect is destroyed via teardown."""
    import asyncio

    from shiny.reactive import invalidate_later

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

    # Collect the asyncio tasks before teardown
    tasks_before = {t for t in asyncio.all_tasks() if not t.done()}

    # Teardown destroys the effect, which invalidates its context,
    # which cancels the invalidate_later task via ctx.on_invalidate
    await proxy.teardown()

    # Give the event loop a tick to process the cancellation
    await asyncio.sleep(0)

    # The invalidate_later task should now be done (cancelled)
    tasks_after = {t for t in asyncio.all_tasks() if not t.done()}
    cancelled_tasks = tasks_before - tasks_after
    assert len(cancelled_tasks) >= 1, "Expected at least one task to be cancelled"

    # Effect should not have run again
    assert exec_count == 1


def test_no_registration_without_session_proxy():
    """Reactive objects created without SessionProxy do NOT register teardown."""
    v = Value(42)
    # Value and Calc still have _torn_down for their own teardown logic
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
    """ExpressStubSession does not have _teardown_callbacks_by_ns."""
    from shiny.express._stub_session import ExpressStubSession

    stub = ExpressStubSession()
    assert not hasattr(stub, "_teardown_callbacks_by_ns")


@pytest.mark.asyncio
async def test_express_stub_session_proxy_teardown_is_silent():
    """SessionProxy created from ExpressStubSession silently does nothing on teardown."""
    from shiny.express._stub_session import ExpressStubSession

    stub = ExpressStubSession()
    proxy = stub.make_scope("mod1")
    assert isinstance(proxy, SessionProxy)

    # on_teardown should not raise even though root has no _teardown_callbacks_by_ns
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
async def test_session_proxy_on_teardown_after_teardown():
    """Registering a callback after teardown creates a fresh callback set for the namespace."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    await proxy.teardown()

    called: list[str] = []
    # Register after teardown — goes into a new AsyncCallbacks for this namespace
    proxy.on_teardown(
        lambda: called.append("late")
    )  # pyright: ignore[reportArgumentType]
    assert called == []

    # A second teardown fires the newly registered callback
    await proxy.teardown()
    assert called == ["late"]


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


# ---------------------------------------------------------------------------
# Module re-creation after teardown
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_module_recreated_after_teardown():
    """A module can be fully re-created under the same namespace after teardown."""
    root = _make_mock_root_session()

    # First lifecycle
    proxy1 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    called_1: list[str] = []
    proxy1.on_teardown(
        lambda: called_1.append("cleanup1")
    )  # pyright: ignore[reportArgumentType]
    await proxy1.teardown()
    assert called_1 == ["cleanup1"]

    # Second lifecycle — same namespace
    proxy2 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    _ = proxy2.input
    _ = proxy2.output

    # New callbacks can be registered and fire independently
    called_2: list[str] = []
    proxy2.on_teardown(
        lambda: called_2.append("cleanup2")
    )  # pyright: ignore[reportArgumentType]
    await proxy2.teardown()

    assert called_2 == ["cleanup2"]
    # First lifecycle's callback was not re-invoked
    assert called_1 == ["cleanup1"]


@pytest.mark.asyncio
async def test_module_recreated_with_new_inputs_outputs():
    """Re-created module gets fresh inputs/outputs after teardown cleaned the old ones."""
    root = _make_mock_root_session()

    # First lifecycle — populate inputs and outputs
    proxy1 = SessionProxy(root_session=root, ns=ResolvedId("panel_1"))
    root.input._map["panel_1-txt"] = Value("old value", read_only=True)
    root.output._outputs["panel_1-plot"] = OutputInfo(
        renderer=_make_mock_renderer(),
        effect=_make_mock_effect(),
        suspend_when_hidden=True,
    )

    await proxy1.teardown()

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

    # Second teardown cleans up the new state
    await proxy2.teardown()
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

    await proxy1.teardown()
    with isolate():
        assert v1.is_set() is False

    # Second lifecycle — new Value under same namespace
    proxy2 = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    with session_context(proxy2):
        v2 = Value(20)

    with isolate():
        assert v2() == 20

    await proxy2.teardown()
    with isolate():
        assert v2.is_set() is False


# ---------------------------------------------------------------------------
# Descendant teardown ordering tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_teardown_cascades_to_child_namespaces():
    """Parent teardown fires callbacks for child namespaces too."""
    root = _make_mock_root_session()
    parent = SessionProxy(root_session=root, ns=ResolvedId("parent"))
    child = SessionProxy(root_session=root, ns=ResolvedId("parent-child"))

    called: list[str] = []
    parent.on_teardown(
        lambda: called.append("parent")
    )  # pyright: ignore[reportArgumentType]
    child.on_teardown(
        lambda: called.append("child")
    )  # pyright: ignore[reportArgumentType]

    await parent.teardown()

    assert "parent" in called
    assert "child" in called


@pytest.mark.asyncio
async def test_teardown_cascades_to_grandchild_namespaces():
    """Parent teardown fires callbacks for grandchild namespaces."""
    root = _make_mock_root_session()
    parent = SessionProxy(root_session=root, ns=ResolvedId("p"))
    child = SessionProxy(root_session=root, ns=ResolvedId("p-c"))
    grandchild = SessionProxy(root_session=root, ns=ResolvedId("p-c-gc"))

    called: list[str] = []
    parent.on_teardown(
        lambda: called.append("parent")
    )  # pyright: ignore[reportArgumentType]
    child.on_teardown(
        lambda: called.append("child")
    )  # pyright: ignore[reportArgumentType]
    grandchild.on_teardown(
        lambda: called.append("grandchild")
    )  # pyright: ignore[reportArgumentType]

    await parent.teardown()

    assert called == ["grandchild", "child", "parent"]


@pytest.mark.asyncio
async def test_teardown_children_before_parents():
    """Deepest namespaces are torn down first (depth-first / reverse construction order)."""
    root = _make_mock_root_session()

    # Register callbacks at various nesting depths
    namespaces = ["a", "a-b", "a-b-c", "a-b-c-d", "a-x"]
    for ns in namespaces:
        proxy = SessionProxy(root_session=root, ns=ResolvedId(ns))
        # Capture ns in default arg to avoid closure issues
        proxy.on_teardown(
            lambda n=ns: order.append(n)
        )  # pyright: ignore[reportArgumentType]

    order: list[str] = []
    top = SessionProxy(root_session=root, ns=ResolvedId("a"))
    await top.teardown()

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
                f"'{ns}' (depth {depth}) — children must be torn down before parents"
            )


@pytest.mark.asyncio
async def test_teardown_does_not_cascade_to_sibling_namespaces():
    """Tearing down 'a' does not affect 'b' even if 'b' has children."""
    root = _make_mock_root_session()
    proxy_a = SessionProxy(root_session=root, ns=ResolvedId("a"))
    proxy_b = SessionProxy(root_session=root, ns=ResolvedId("b"))
    proxy_b_child = SessionProxy(root_session=root, ns=ResolvedId("b-child"))

    called: list[str] = []
    proxy_a.on_teardown(
        lambda: called.append("a")
    )  # pyright: ignore[reportArgumentType]
    proxy_b.on_teardown(
        lambda: called.append("b")
    )  # pyright: ignore[reportArgumentType]
    proxy_b_child.on_teardown(
        lambda: called.append("b-child")
    )  # pyright: ignore[reportArgumentType]

    await proxy_a.teardown()

    assert called == ["a"]
    # b and b-child callbacks still registered
    assert "b" in cast(Any, root)._teardown_callbacks_by_ns
    assert "b-child" in cast(Any, root)._teardown_callbacks_by_ns


@pytest.mark.asyncio
async def test_child_teardown_does_not_cascade_to_parent():
    """Tearing down a child does not fire parent callbacks."""
    root = _make_mock_root_session()
    parent = SessionProxy(root_session=root, ns=ResolvedId("parent"))
    child = SessionProxy(root_session=root, ns=ResolvedId("parent-child"))

    called: list[str] = []
    parent.on_teardown(
        lambda: called.append("parent")
    )  # pyright: ignore[reportArgumentType]
    child.on_teardown(
        lambda: called.append("child")
    )  # pyright: ignore[reportArgumentType]

    await child.teardown()

    assert called == ["child"]
    # Parent callbacks still registered
    assert "parent" in cast(Any, root)._teardown_callbacks_by_ns


# ---------------------------------------------------------------------------
# Input/output teardown ordering tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_inputs_available_during_teardown_callbacks():
    """Input values can still be read inside teardown callbacks."""
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

    proxy.on_teardown(read_input)
    await proxy.teardown()

    # The callback should have been able to read the input value
    assert observed_value == ["hello"]
    # After teardown completes, the input is removed
    assert "mod1-txt" not in root.input._map


@pytest.mark.asyncio
async def test_outputs_available_during_teardown_callbacks():
    """Output entries still exist during teardown callbacks."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    mock_effect = _make_mock_effect()
    root.output._outputs["mod1-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=mock_effect, suspend_when_hidden=True
    )

    output_existed: list[bool] = []

    def check_output() -> None:
        output_existed.append("mod1-plot" in root.output._outputs)

    proxy.on_teardown(check_output)
    await proxy.teardown()

    # Output was still present when the callback ran
    assert output_existed == [True]
    # After teardown completes, the output is removed
    assert "mod1-plot" not in root.output._outputs
