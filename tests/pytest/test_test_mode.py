"""Tests for Shiny test mode (Phase A)."""

from __future__ import annotations

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

    with pytest.raises(RuntimeError):
        export_test_values(foo=lambda: 1)


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
    session.export_test_values(myexp=lambda: 123)

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

    session.export_test_values(bad_value=lambda: Bad(), raises=raises)

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
    session.export_test_values(exp=lambda: 7)

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
    session.export_test_values(exp=lambda: calls.append(1) or 1)

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
