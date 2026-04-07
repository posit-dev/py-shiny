"""Tests for reactive teardown behavior."""

import pytest

from shiny._namespaces import ResolvedId
from shiny.reactive import DestroyedReactiveError, Value, calc, effect, flush, isolate
from shiny.session._session import Inputs, OutputInfo, Outputs, SessionProxy
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
    shared_map: dict[str, Value] = {}
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
    shared_map: dict[str, Value] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    shared_map[".clientdata_output_panel_1-my_plot_hidden"] = Value(False, read_only=True)
    shared_map[".clientdata_output_panel_1-my_plot_width"] = Value(800, read_only=True)
    shared_map[".clientdata_output_panel_1-my_plot_height"] = Value(600, read_only=True)

    inputs._teardown()

    assert ".clientdata_output_panel_1-my_plot_hidden" not in shared_map
    assert ".clientdata_output_panel_1-my_plot_width" not in shared_map
    assert ".clientdata_output_panel_1-my_plot_height" not in shared_map


def test_inputs_teardown_preserves_global_clientdata():
    """_teardown() does NOT remove global clientdata keys."""
    shared_map: dict[str, Value] = {}
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
    shared_map: dict[str, Value] = {}
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
    shared_map: dict[str, Value] = {}
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
    shared_map: dict[str, Value] = {}
    ns = ResolvedId("panel_1")
    inputs = Inputs(values=shared_map, ns=ns)

    shared_map["panel_1-txt"] = Value("old", read_only=True)
    inputs._teardown()
    assert "panel_1-txt" not in shared_map

    new_value = Value(read_only=True)
    new_value._set("new")
    shared_map["panel_1-txt"] = new_value

    with isolate():
        assert shared_map["panel_1-txt"]() == "new"


def _make_mock_effect():
    """Create a minimal mock that tracks destroy() calls."""

    class MockEffect:
        def __init__(self):
            self._destroyed = False

        def destroy(self):
            self._destroyed = True

    return MockEffect()


def _make_mock_renderer():
    """Create a minimal mock renderer."""

    class MockRenderer:
        pass

    return MockRenderer()


class _StubSession:
    """Minimal session stub for Outputs constructor."""

    def __init__(self):
        self.ns = ResolvedId("")

    def _is_hidden(self, name: str) -> bool:
        return False


def test_outputs_teardown_removes_namespaced_outputs():
    """_teardown() removes all outputs matching namespace prefix."""
    shared_outputs: dict[str, OutputInfo] = {}
    ns = ResolvedId("panel_1")
    session = _StubSession()
    outputs = Outputs(session, ns=ns, outputs=shared_outputs)

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
    session = _StubSession()
    outputs = Outputs(session, ns=ns, outputs=shared_outputs)

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
    assert not effect2._destroyed


def test_outputs_teardown_destroys_effects():
    """_teardown() calls destroy() on each removed output's effect."""
    shared_outputs: dict[str, OutputInfo] = {}
    ns = ResolvedId("panel_1")
    session = _StubSession()
    outputs = Outputs(session, ns=ns, outputs=shared_outputs)

    effect1 = _make_mock_effect()
    shared_outputs["panel_1-plot"] = OutputInfo(
        renderer=_make_mock_renderer(), effect=effect1, suspend_when_hidden=True
    )

    outputs._teardown()

    assert effect1._destroyed is True


def _make_mock_root_session():
    """Create a minimal mock root session for SessionProxy tests."""

    class MockApp:
        pass

    class MockOutboundQueues:
        pass

    class MockBookmark:
        def __init__(self):
            self._on_get_exclude: list = []

    class MockRootSession:
        def __init__(self):
            self.app = MockApp()
            self.id = "mock_session_id"
            self.ns = ResolvedId("")
            self.input = Inputs(values={}, ns=ResolvedId(""))
            self.output = Outputs(self, ns=ResolvedId(""), outputs={})
            self._outbound_message_queues = MockOutboundQueues()
            self._downloads = {}
            self.bookmark = MockBookmark()

        def _is_hidden(self, name: str) -> bool:
            return False

        def is_stub_session(self) -> bool:
            return True

        def make_scope(self, id):
            return SessionProxy(root_session=self, ns=ResolvedId(str(id)))

        def root_scope(self):
            return self

    return MockRootSession()


def test_session_proxy_on_teardown_fires_callbacks():
    """on_teardown() registers callbacks that fire on teardown()."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    called = []
    proxy.on_teardown(lambda: called.append("a"))
    proxy.on_teardown(lambda: called.append("b"))

    proxy.teardown()

    assert called == ["a", "b"]


def test_session_proxy_teardown_is_idempotent():
    """Second teardown() call does nothing."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    call_count = 0

    def cb():
        nonlocal call_count
        call_count += 1

    proxy.on_teardown(cb)
    proxy.teardown()
    assert call_count == 1

    proxy.teardown()
    assert call_count == 1


def test_session_proxy_teardown_clears_callbacks():
    """Callbacks list is cleared after teardown (no reference retention)."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    large_obj = [0] * 10000
    proxy.on_teardown(lambda: large_obj)

    proxy.teardown()
    assert len(proxy._on_teardown_callbacks) == 0


def test_session_proxy_teardown_guards_input():
    """After teardown, accessing session.input raises RuntimeError."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    proxy.teardown()

    with pytest.raises(RuntimeError, match="torn down"):
        _ = proxy.input


def test_session_proxy_teardown_guards_output():
    """After teardown, accessing session.output raises RuntimeError."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))
    proxy.teardown()

    with pytest.raises(RuntimeError, match="torn down"):
        _ = proxy.output


def _make_mock_root_session_non_stub():
    """Mock root session where is_stub_session() returns False (for Effect_ tests)."""

    class MockApp:
        pass

    class MockOutboundQueues:
        pass

    class MockBookmark:
        def __init__(self):
            self._on_get_exclude: list = []

    class MockRootSession:
        def __init__(self):
            self.app = MockApp()
            self.id = "mock_session_id"
            self.ns = ResolvedId("")
            self.input = Inputs(values={}, ns=ResolvedId(""))
            self.output = Outputs(self, ns=ResolvedId(""), outputs={})
            self._outbound_message_queues = MockOutboundQueues()
            self._downloads = {}
            self.bookmark = MockBookmark()

        def _is_hidden(self, name: str) -> bool:
            return False

        def is_stub_session(self) -> bool:
            return False

        def on_ended(self, fn):
            pass  # No-op for testing

        def _increment_busy_count(self):
            pass

        def _decrement_busy_count(self):
            pass

        def make_scope(self, id):
            return SessionProxy(root_session=self, ns=ResolvedId(str(id)))

        def root_scope(self):
            return self

    return MockRootSession()


def test_value_self_registers_with_session_proxy():
    """Value created within SessionProxy context registers _teardown."""
    root = _make_mock_root_session()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    with session_context(proxy):
        v = Value(42)

    proxy.teardown()
    with isolate():
        assert v.is_set() is False


def test_calc_self_registers_with_session_proxy():
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

    proxy.teardown()

    with pytest.raises(DestroyedReactiveError):
        with isolate():
            doubled()


def test_effect_self_registers_with_session_proxy():
    """Effect_ created within SessionProxy context registers destroy."""
    root = _make_mock_root_session_non_stub()
    proxy = SessionProxy(root_session=root, ns=ResolvedId("mod1"))

    with session_context(proxy):
        @effect()
        def my_effect():
            pass

    proxy.teardown()
    assert my_effect._destroyed is True


def test_no_registration_without_session_proxy():
    """Reactive objects created without SessionProxy do NOT register teardown."""
    v = Value(42)
    assert v._torn_down is False

    @calc()
    def doubled():
        return v() * 2

    assert doubled._torn_down is False
