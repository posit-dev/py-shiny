"""Tests for Shiny test mode (Phase A)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest
from starlette.requests import Request
from starlette.responses import Response

from shiny import App, reactive, ui
from shiny._connection import MockConnection
from shiny._utils import is_test_mode
from shiny.session._session import AppSession, OutBoundMessageQueues
from shiny.session._utils import (
    session_context,
)
from shiny.testmode import export_test_values


def test_is_test_mode_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    assert is_test_mode() is False

    monkeypatch.setenv("SHINY_TESTMODE", "1")
    assert is_test_mode() is True

    monkeypatch.setenv("SHINY_TESTMODE", "0")
    assert is_test_mode() is False

    monkeypatch.setenv("SHINY_TESTMODE", "true")
    assert is_test_mode() is False


def test_app_reads_test_mode_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    app_on = App(ui.TagList(), None)
    assert app_on._test_mode is True

    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    app_off = App(ui.TagList(), None)
    assert app_off._test_mode is False


def _make_app_session() -> AppSession:
    """Create a real AppSession backed by a MockConnection.

    Construct AFTER setting/clearing SHINY_TESTMODE so `app._test_mode` reflects
    the desired state.
    """
    conn = MockConnection()
    return App(ui.TagList(), None)._create_session(conn)


def _snapshot_request(query_string: bytes = b"") -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "headers": [],
            "query_string": query_string,
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


def test_outbound_queue_set_silent_retains_last_value() -> None:
    omq = OutBoundMessageQueues(record_test_values=True)
    omq.set_value("out1", 42)

    omq.set_silent("out1")

    # Transient queues: silenced like any other value (client should clear it).
    assert omq.values["out1"] is None
    assert "out1" not in omq.errors
    # Persistent test-mode record: untouched, still reports the last value.
    assert omq.test_values == {"out1": 42}
    assert omq.test_errors == {}


def test_outbound_queue_set_silent_retains_last_error() -> None:
    omq = OutBoundMessageQueues(record_test_values=True)
    omq.set_error("out1", {"message": "boom"})

    omq.set_silent("out1")

    assert omq.values["out1"] is None
    assert "out1" not in omq.errors
    # Persistent test-mode record: untouched, still reports the last error.
    assert omq.test_errors == {"out1": {"message": "boom"}}
    assert "out1" not in omq.test_values


def test_outbound_queue_set_silent_on_first_run_leaves_absent() -> None:
    omq = OutBoundMessageQueues(record_test_values=True)

    omq.set_silent("out1")

    assert omq.values["out1"] is None
    assert "out1" not in omq.test_values
    assert "out1" not in omq.test_errors


def test_app_session_wires_record_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()
    assert session._outbound_message_queues._record_test_values is True

    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    session_off = _make_app_session()
    assert session_off._outbound_message_queues._record_test_values is False


def test_export_test_values_registers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    with session_context(session):
        export_test_values(foo=lambda: 1, bar=lambda: 2)
    assert set(session._test_value_exports) == {"foo", "bar"}

    # last-registration-wins on duplicate name
    with session_context(session):
        export_test_values(foo=lambda: 99)
    assert session._test_value_exports["foo"]() == 99


def test_export_test_values_noop_when_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    session = _make_app_session()
    with session_context(session):
        export_test_values(foo=lambda: 1)
    assert session._test_value_exports == {}


def test_export_test_values_namespaced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    root = _make_app_session()
    proxy = root.make_scope("mod1")
    with session_context(proxy):
        export_test_values(foo=lambda: 1)
    # DEVIATION from R: export names are namespaced with the module prefix.
    assert "mod1-foo" in root._test_value_exports
    assert "foo" not in root._test_value_exports


def test_export_test_values_targets_other_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    other = _make_app_session()
    # No active session here; target `other` explicitly via its context.
    with session_context(other):
        export_test_values(bar=lambda: 2)
    assert "bar" in other._test_value_exports


def test_export_test_values_requires_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    with pytest.raises(RuntimeError):
        export_test_values(foo=lambda: 1)


def test_session_export_test_values_method(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Directly exercise the private `Session._export_test_values` method that the
    # public `export_test_values()` delegates to (no active-session context
    # needed since the method operates on the session object itself).
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    root = _make_app_session()

    # AppSession stores names as-is.
    root._export_test_values(foo=lambda: 1)
    assert "foo" in root._test_value_exports

    # SessionProxy namespaces names with the module prefix, into the root session.
    proxy = root.make_scope("mod1")
    proxy._export_test_values(bar=lambda: 2)
    assert "mod1-bar" in root._test_value_exports
    assert "bar" not in root._test_value_exports

    # No-op when test mode is off.
    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    off = _make_app_session()
    off._export_test_values(baz=lambda: 3)
    assert off._test_value_exports == {}


def test_is_internal_snapshot_input() -> None:
    from shiny.session._session import _is_internal_snapshot_input

    assert _is_internal_snapshot_input(".clientdata_output_x_hidden") is True
    assert _is_internal_snapshot_input(".shinybookmarkstate") is False  # not the id
    assert _is_internal_snapshot_input("x") is False


@pytest.mark.asyncio
async def test_serialize_test_mode_collects_and_skips() -> None:
    from shiny.session._session import Inputs

    inputs = Inputs(dict())
    inputs["x"] = reactive.Value(5)
    inputs["name"] = reactive.Value("hi")
    inputs[".clientdata_output_x_hidden"] = reactive.Value(True)

    result = await inputs._serialize_test_mode()
    assert result == {"x": 5, "name": "hi"}


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


def test_get_test_snapshot_url() -> None:
    session = _make_app_session()
    url = session.get_test_snapshot_url()
    assert url.startswith(f"session/{session.id}/dataobj/shinytest?nonce=")

    # Proxy delegates to the root session (no namespacing of the URL)
    proxy = session.make_scope("mod1")
    purl = proxy.get_test_snapshot_url()
    assert purl.startswith(f"session/{session.id}/dataobj/shinytest?nonce=")


@pytest.mark.asyncio
async def test_snapshot_endpoint_returns_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    session.input["x"] = reactive.Value(10)
    session._outbound_message_queues.set_value("out1", "hello")
    session._outbound_message_queues.set_error("out2", {"message": "boom"})
    with session_context(session):
        export_test_values(myexp=lambda: 123)

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
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
async def test_snapshot_endpoint_silence_after_value_retains_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    session._outbound_message_queues.set_value("out1", "hello")
    session._outbound_message_queues.set_silent("out1")

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    assert body["output"]["out1"] == "hello"


@pytest.mark.asyncio
async def test_snapshot_endpoint_silence_after_error_retains_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    session._outbound_message_queues.set_error("out1", {"message": "boom"})
    session._outbound_message_queues.set_silent("out1")

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    assert body["output"]["out1"] == {"__shiny_output_error__": "boom"}


@pytest.mark.asyncio
async def test_snapshot_endpoint_silence_on_first_run_omits_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    session._outbound_message_queues.set_silent("out1")

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    assert "out1" not in body["output"]


@pytest.mark.asyncio
async def test_snapshot_endpoint_404_when_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    session = _make_app_session()
    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
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

    with session_context(session):
        export_test_values(bad_value=lambda: Bad(), raises=raises)

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    assert "__shiny_serialization_error__" in body["export"]["bad_value"]
    assert "__shiny_serialization_error__" in body["export"]["raises"]


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


@pytest.mark.asyncio
async def test_snapshot_endpoint_handles_resolved_id_output_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Output ids are `ResolvedId` (a `str` subclass). orjson rejects `str`
    # subclasses as dict keys ("Dict key must be str"), so the snapshot handler
    # must coerce them to plain `str` before serializing.
    import orjson

    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    key = session.ns("greeting")
    assert type(key) is not str  # ResolvedId, not a plain str
    session._outbound_message_queues.set_value(key, "hi")

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    body = orjson.loads(resp.body)
    assert body["output"]["greeting"] == "hi"


@pytest.mark.asyncio
async def test_snapshot_endpoint_format_param(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    # `format=json` (and the default) are accepted.
    ok = cast(
        Response,
        await session._handle_request_impl(
            _snapshot_request(b"format=json"), "dataobj", "shinytest"
        ),
    )
    assert ok.status_code == 200

    # Any other format (including R's `rds`) is rejected.
    bad = cast(
        Response,
        await session._handle_request_impl(
            _snapshot_request(b"format=rds"), "dataobj", "shinytest"
        ),
    )
    assert bad.status_code == 400


@pytest.mark.asyncio
async def test_snapshot_endpoint_block_filtering(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import orjson

    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()
    session.input["x"] = reactive.Value(1)
    session._outbound_message_queues.set_value("out1", "a")
    session._outbound_message_queues.set_value("out2", "b")
    with session_context(session):
        export_test_values(exp=lambda: 7)

    async def snap(qs: bytes) -> dict[str, object]:
        resp = cast(
            Response,
            await session._handle_request_impl(
                _snapshot_request(qs), "dataobj", "shinytest"
            ),
        )
        return orjson.loads(resp.body)

    # No params -> all three blocks (py-shiny convenience default; R returns 400).
    allb = await snap(b"")
    assert set(allb.keys()) == {"input", "output", "export"}

    # Selective: only the requested block(s) appear; "1" = the whole block.
    only_out = await snap(b"output=1")
    assert set(only_out.keys()) == {"output"}
    assert only_out["output"] == {"out1": "a", "out2": "b"}

    two = await snap(b"input=1&export=1")
    assert set(two.keys()) == {"input", "export"}

    # A comma list selects specific keys; unknown names are dropped.
    csv = await snap(b"output=out1,nope")
    assert set(csv.keys()) == {"output"}
    assert csv["output"] == {"out1": "a"}

    # An empty value selects no keys (matches R: "" splits to nothing).
    empty = await snap(b"output=")
    assert empty == {"output": {}}


@pytest.mark.asyncio
async def test_snapshot_endpoint_skips_unrequested_blocks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Export callables must not be evaluated when the `export` block is not
    # requested (building only requested blocks avoids unnecessary work/side
    # effects).
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()
    calls: list[int] = []
    with session_context(session):
        export_test_values(exp=lambda: calls.append(1) or 1)

    await session._handle_request_impl(
        _snapshot_request(b"input=1"), "dataobj", "shinytest"
    )
    assert calls == []  # export not requested -> callable not invoked

    await session._handle_request_impl(
        _snapshot_request(b"export=1"), "dataobj", "shinytest"
    )
    assert calls == [1]  # export requested -> callable invoked once


@pytest.mark.asyncio
async def test_snapshot_endpoint_sortc_param(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    # `sortC=1` and an absent `sortC` are accepted (keys are always C-sorted).
    for qs in (b"input=1&sortC=1", b"input=1"):
        resp = cast(
            Response,
            await session._handle_request_impl(
                _snapshot_request(qs), "dataobj", "shinytest"
            ),
        )
        assert resp.status_code == 200

    # Any other `sortC` value is rejected (mirrors R).
    bad = cast(
        Response,
        await session._handle_request_impl(
            _snapshot_request(b"input=1&sortC=2"), "dataobj", "shinytest"
        ),
    )
    assert bad.status_code == 400


def test_export_test_values_relocated() -> None:
    # `export_test_values` lives in `shiny.testmode`; the pre-release
    # `shiny.session` location is gone (PR #2270 was never released).
    import shiny.session

    assert not hasattr(shiny.session, "export_test_values")
    assert "export_test_values" not in shiny.session.__all__


@pytest.mark.asyncio
async def test_input_snapshot_preprocess_applied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()
    session.input["t"] = reactive.Value("2026-07-02 12:34:56")
    session.input["x"] = reactive.Value(10)

    # Sync preprocessor
    session.input.set_snapshot_preprocess("t", lambda value: "<time>")

    # Async preprocessor
    async def double(value: int) -> int:
        return value * 2

    session.input.set_snapshot_preprocess("x", double)

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    assert body["input"]["t"] == "<time>"
    assert body["input"]["x"] == 20


@pytest.mark.asyncio
async def test_input_snapshot_preprocess_namespaced(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()
    from shiny._namespaces import ResolvedId

    session.input[ResolvedId("mod1-y")] = reactive.Value(1)

    # Registering through a module proxy namespaces the id and shares storage
    # with the root session's Inputs.
    proxy = session.make_scope("mod1")
    proxy.input.set_snapshot_preprocess("y", lambda value: value + 100)

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    assert body["input"]["mod1-y"] == 101


@pytest.mark.asyncio
async def test_input_snapshot_preprocess_error_marker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()
    session.input["bad"] = reactive.Value(1)
    session.input["ok"] = reactive.Value(2)

    def boom(value: int) -> int:
        raise RuntimeError("boom")

    session.input.set_snapshot_preprocess("bad", boom)

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    # A raising preprocessor becomes a visible, non-fatal marker; other keys
    # are unaffected.
    assert body["input"]["bad"] == {"__shiny_snapshot_preprocess_error__": "boom"}
    assert body["input"]["ok"] == 2


@pytest.mark.asyncio
async def test_input_snapshot_preprocess_reregister_overwrites(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()
    session.input["x"] = reactive.Value(1)

    session.input.set_snapshot_preprocess("x", lambda value: "first")
    session.input.set_snapshot_preprocess("x", lambda value: "second")

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    assert body["input"]["x"] == "second"


@pytest.mark.asyncio
async def test_output_snapshot_preprocess_applied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    from shiny import render

    @render.text
    def out1() -> str:
        return "unused"

    session.output(out1)

    # Sync preprocessor; simulate the output having rendered.
    out1.snapshot_preprocess(lambda value: "<scrubbed>")
    session._outbound_message_queues.set_value("out1", "the time is 12:34")

    @render.text
    def out2() -> str:
        return "unused"

    session.output(out2)

    # Async preprocessor
    async def shout(value: str) -> str:
        return value.upper()

    out2.snapshot_preprocess(shout)
    session._outbound_message_queues.set_value("out2", "hello")

    # An output with no preprocessor passes through unchanged, as does a
    # recorded value with no registered renderer at all.
    session._outbound_message_queues.set_value("out3", "raw")

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    assert body["output"]["out1"] == "<scrubbed>"
    assert body["output"]["out2"] == "HELLO"
    assert body["output"]["out3"] == "raw"


@pytest.mark.asyncio
async def test_output_snapshot_preprocess_error_marker_and_bypass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    from shiny import render

    @render.text
    def bad() -> str:
        return "unused"

    session.output(bad)

    def boom(value: str) -> str:
        raise RuntimeError("boom")

    bad.snapshot_preprocess(boom)
    session._outbound_message_queues.set_value("bad", "value")

    # Errored outputs keep their error marker; the preprocessor must NOT run
    # on them.
    @render.text
    def errored() -> str:
        return "unused"

    session.output(errored)
    errored.snapshot_preprocess(lambda value: "SHOULD NOT APPEAR")
    session._outbound_message_queues.set_error("errored", {"message": "kaput"})

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    assert body["output"]["bad"] == {"__shiny_snapshot_preprocess_error__": "boom"}
    assert body["output"]["errored"] == {"__shiny_output_error__": "kaput"}


@pytest.mark.asyncio
async def test_snapshot_preprocess_free_functions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()
    session.input["x"] = reactive.Value(1)

    from shiny import render
    from shiny.testmode import snapshot_preprocess_input, snapshot_preprocess_output

    @render.text
    def out1() -> str:
        return "unused"

    session.output(out1)
    session._outbound_message_queues.set_value("out1", "hello")

    with session_context(session):
        snapshot_preprocess_input("x", lambda value: value + 1)
        snapshot_preprocess_output("out1", lambda value: value.upper())

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    assert body["input"]["x"] == 2
    assert body["output"]["out1"] == "HELLO"


def test_snapshot_preprocess_output_unregistered_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    from shiny.testmode import snapshot_preprocess_output

    with session_context(session):
        with pytest.raises(ValueError, match="No output named 'nope'"):
            snapshot_preprocess_output("nope", lambda value: value)


def test_snapshot_preprocess_free_functions_require_session() -> None:
    from shiny.testmode import snapshot_preprocess_input, snapshot_preprocess_output

    with pytest.raises(RuntimeError):
        snapshot_preprocess_input("x", lambda value: value)
    with pytest.raises(RuntimeError):
        snapshot_preprocess_output("x", lambda value: value)


def test_snapshot_preprocess_file_input_helper() -> None:
    from shiny.testmode import _snapshot_preprocess_file_input

    value = [
        {
            "name": "a.txt",
            "size": 1,
            "type": "text/plain",
            "datapath": "/tmp/xyz123/a.txt",
        },
        {"name": "b.txt", "size": 2, "type": "text/plain", "datapath": "b.txt"},
    ]
    scrubbed = _snapshot_preprocess_file_input(value)
    assert [f["datapath"] for f in scrubbed] == ["a.txt", "b.txt"]
    # Original value is not mutated.
    assert value[0]["datapath"] == "/tmp/xyz123/a.txt"

    # Non-list / malformed values pass through unchanged.
    assert _snapshot_preprocess_file_input(None) is None
    assert _snapshot_preprocess_file_input("x") == "x"
    assert _snapshot_preprocess_file_input([{"name": "no-path"}]) == [
        {"name": "no-path"}
    ]


@pytest.mark.asyncio
async def test_upload_end_auto_registers_file_scrub(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    class FakeOp:
        def finish(self) -> list[dict[str, object]]:
            return [
                {
                    "name": "a.txt",
                    "size": 1,
                    "type": "text/plain",
                    "datapath": "/tmp/xyz123/a.txt",
                }
            ]

    def fake_get_upload_operation(job_id: str) -> FakeOp:
        return FakeOp()

    monkeypatch.setattr(
        session._file_upload_manager,
        "get_upload_operation",
        fake_get_upload_operation,
    )
    handler, _ = session._message_handlers["uploadEnd"]
    await handler("job1", "file1")

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    # The live input value keeps the real tempdir path; only the snapshot is
    # scrubbed to the basename (matching R's snapshotPreprocessorFileInput).
    assert body["input"]["file1"] == [
        {"name": "a.txt", "size": 1, "type": "text/plain", "datapath": "a.txt"}
    ]


@pytest.mark.asyncio
async def test_snapshot_preprocess_output_namespaced(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()
    proxy = session.make_scope("mod1")

    from shiny import render
    from shiny.testmode import snapshot_preprocess_output

    @render.text
    def out1() -> str:
        return "unused"

    # Register through the module proxy: the output lands under the
    # namespaced name, and the free function resolves the plain id against
    # the proxy's namespace.
    proxy.output(out1)
    session._outbound_message_queues.set_value("mod1-out1", "hello")

    with session_context(proxy):
        snapshot_preprocess_output("out1", lambda value: value.upper())

    resp = cast(
        Response,
        await session._handle_request_impl(_snapshot_request(), "dataobj", "shinytest"),
    )
    import orjson

    body = orjson.loads(resp.body)
    assert body["output"]["mod1-out1"] == "HELLO"


def test_file_restore_handler_registers_snapshot_preprocess(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # The `shiny.file` input handler (bookmark restore) must register the same
    # datapath scrubber as `uploadEnd`.
    import shiny.bookmark._restore_state
    import shiny.input_handler
    from shiny._namespaces import ResolvedId

    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()

    (tmp_path / "a.txt").write_text("hello")

    def fake_can_serialize_input_file(session: object) -> bool:
        return True

    monkeypatch.setattr(
        shiny.input_handler, "can_serialize_input_file", fake_can_serialize_input_file
    )
    monkeypatch.setattr(
        shiny.bookmark._restore_state,
        "get_current_restore_context",
        lambda: SimpleNamespace(dir=str(tmp_path)),
    )

    handler = shiny.input_handler.input_handlers["shiny.file"]
    value = {
        "name": ["a.txt"],
        "size": [5],
        "type": ["text/plain"],
        "datapath": ["a.txt"],
    }
    restored = handler(value, ResolvedId("file1"), session)

    assert isinstance(restored, list) and len(restored) == 1
    assert ResolvedId("file1") in session.input._snapshot_preprocessors
