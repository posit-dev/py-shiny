"""Tests for `shiny.Session`."""

import asyncio
import json
from typing import NamedTuple

import numpy as np
import orjson
import pytest

from shiny import App, Inputs, Outputs, Session, module, ui
from shiny._connection import MockConnection
from shiny.express._stub_session import ExpressStubSession
from shiny.reactive import effect, flush, isolate
from shiny.types import SilentException


def test_stub_session_user_groups():
    from shiny.express._stub_session import ExpressStubSession

    stub = ExpressStubSession()
    assert stub.user is None
    assert stub.groups is None


@pytest.mark.asyncio
async def test_module_session_user_groups():
    """SessionProxy (module session) should delegate user/groups to the root session."""
    captured: dict[str, object] = {}

    @module.server
    def mod(input: Inputs, output: Outputs, session: Session):
        captured["mod_user"] = session.user
        captured["mod_groups"] = session.groups

    def server(input: Inputs, output: Outputs, session: Session):
        mod("m")
        captured["root_user"] = session.user
        captured["root_groups"] = session.groups

    creds = json.dumps({"user": "alice", "groups": ["admin", "dev"]}).encode()
    headers = [(b"shiny-server-credentials", creds)]
    conn = MockConnection()
    conn._http_conn.scope["headers"] = headers
    sess = App(ui.TagList(), server)._create_session(conn)

    async def mock_client():
        conn.cause_receive('{"method":"init","data":{}}')
        conn.cause_disconnect()

    await asyncio.gather(mock_client(), sess._run())

    assert captured["root_user"] == "alice"
    assert captured["root_groups"] == ["admin", "dev"]
    assert captured["mod_user"] == "alice"
    assert captured["mod_groups"] == ["admin", "dev"]


@pytest.mark.parametrize("method", [1, ["a"], None])
@pytest.mark.asyncio
async def test_non_string_method_closes_session(
    method: object, capsys: pytest.CaptureFixture[str]
):
    conn = MockConnection()
    sess = App(ui.TagList(), None)._create_session(conn)
    conn.cause_receive(json.dumps({"method": method, "tag": 1, "args": []}))

    # `_run()` returning means the session ended.
    await asyncio.wait_for(sess._run(), timeout=5)

    err = capsys.readouterr().err
    assert "Message 'method' must be a string." in err
    assert "Traceback" not in err


@pytest.mark.parametrize("message", ["1", "null", '"method"', "[]"])
@pytest.mark.asyncio
async def test_non_object_message_closes_session(
    message: str, capsys: pytest.CaptureFixture[str]
):
    conn = MockConnection()
    sess = App(ui.TagList(), None)._create_session(conn)
    conn.cause_receive(message)

    # `_run()` returning means the session ended.
    await asyncio.wait_for(sess._run(), timeout=5)

    err = capsys.readouterr().err
    assert "Message does not contain 'method'." in err
    assert "Traceback" not in err


@pytest.mark.asyncio
async def test_send_message_non_finite_floats_are_null():
    # A bare `NaN`/`Infinity` token is not JSON: the browser's `JSON.parse()` throws
    text = await sent_text({"custom": {"x": {"a": float("nan"), "b": float("inf")}}})

    assert strict_json_loads(text) == {"custom": {"x": {"a": None, "b": None}}}


@pytest.mark.asyncio
async def test_send_message_embeds_pre_encoded_json():
    text = await sent_text(
        {"values": {"df": {"data": orjson.Fragment(b'[[1,"a"],[2,"b"]]')}}}
    )

    assert strict_json_loads(text) == {"values": {"df": {"data": [[1, "a"], [2, "b"]]}}}


class Point(NamedTuple):
    x: int
    y: int


@pytest.mark.parametrize(
    ("value", "want"),
    [
        ({1: "a"}, {"1": "a"}),
        (2**70, 1180591620717411303424),
        (np.float64(1.5), 1.5),
        (Point(1, 2), [1, 2]),
        ("\ud800", "\ud800"),
    ],
    ids=[
        "non-str key",
        "int beyond 64 bits",
        "float subclass",
        "namedtuple",
        "lone surrogate",
    ],
)
@pytest.mark.asyncio
async def test_send_message_values_only_the_stdlib_encoder_accepts(
    value: object, want: object
):
    text = await sent_text({"custom": {"x": value}})

    assert strict_json_loads(text) == {"custom": {"x": want}}


@pytest.mark.asyncio
async def test_send_message_pre_encoded_json_beside_stdlib_only_value():
    # One batched message can hold a data frame's rows and another output's value
    text = await sent_text({"values": {"df": orjson.Fragment(b"[[1]]"), "n": 2**70}})

    assert strict_json_loads(text) == {
        "values": {"df": [[1]], "n": 1180591620717411303424}
    }


class RecordingConnection(MockConnection):
    def __init__(self):
        super().__init__()
        self.sent: list[str] = []

    async def send(self, message: str) -> None:
        self.sent.append(message)


async def sent_text(message: dict[str, object]) -> str:
    """The text `AppSession._send_message()` puts on the wire for `message`."""
    conn = RecordingConnection()
    sess = App(ui.TagList(), None)._create_session(conn)
    await sess._send_message(message)
    (text,) = conn.sent
    return text


def strict_json_loads(text: str) -> object:
    """`json.loads()`, but rejecting the non-JSON tokens `NaN` and `Infinity`."""

    def reject(token: str) -> object:
        raise ValueError(f"{token} is not valid JSON")

    return json.loads(text, parse_constant=reject)


def test_require_active_session_error_messages():
    # require_active_session() should report the caller's name when an error occurs.
    with pytest.raises(RuntimeError, match=r"Progress\(\) must be called"):
        ui.Progress()

    with pytest.raises(RuntimeError, match=r"notification.remove\(\) must be called.*"):
        ui.notification_remove("abc")


def test_allow_reconnect():
    sent: list[dict[str, object]] = []

    def record(message: dict[str, object]) -> None:
        sent.append(message)

    session = ExpressStubSession()
    session._send_message_sync = record

    session.allow_reconnect(True)
    session.allow_reconnect(False)
    session.allow_reconnect("force")
    assert sent == [
        {"allowReconnect": True},
        {"allowReconnect": False},
        {"allowReconnect": "force"},
    ]

    for value in ("TRUE", 1, None):
        with pytest.raises(ValueError, match="must be"):
            session.allow_reconnect(value)  # pyright: ignore[reportArgumentType]

    # Invalid values shouldn't have sent anything more.
    assert len(sent) == 3


def test_input_readonly():
    input = Inputs({})

    with isolate():
        with pytest.raises(RuntimeError):
            input.x.set(1)


def test_input_nonexistent():
    # Make sure that if you try to access an input that doesn't exist, it:
    # - Raises a SilentException
    # - Appears _not_ to add the item to the Inputs object (even though under the hood,
    #   it does actually add it)
    input = Inputs({})

    with isolate():
        assert "x" not in input
        with pytest.raises(SilentException):
            input.x()
        assert "x" not in input
        with pytest.raises(SilentException):
            input.x()

    with isolate():
        with pytest.raises(SilentException):
            input.y()
        assert "y" not in input
        with pytest.raises(SilentException):
            input.y()
        assert "y" not in input


@pytest.mark.asyncio
async def test_input_nonexistent_deps():
    # Make sure that `"x" in input` causes a reactive dependency to be created.
    input = Inputs({})
    result = None

    @effect()
    def o1():
        nonlocal result
        result = "x" in input

    await flush()
    assert result is False
    assert o1._exec_count == 1

    # This should invalidate o1 and cause it to re-execute on the next flush().
    input.x._set(1)
    await flush()
    assert result is True
    assert o1._exec_count == 2

    # This shouldn't invalidate o1, because it doesn't change the status of x's
    # existence. (x already exists; this just changes its value.)
    input.x._set(2)
    await flush()
    assert result is True
    assert o1._exec_count == 2
