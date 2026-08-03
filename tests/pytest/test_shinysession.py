"""Tests for `shiny.Session`."""

import asyncio
import json

import pytest

from shiny import App, Inputs, Outputs, Session, module, ui
from shiny._connection import MockConnection
from shiny.reactive import effect, flush, isolate
from shiny.session import Inputs
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


def test_require_active_session_error_messages():
    # require_active_session() should report the caller's name when an error occurs.
    with pytest.raises(RuntimeError, match=r"Progress\(\) must be called"):
        ui.Progress()

    with pytest.raises(RuntimeError, match=r"notification.remove\(\) must be called.*"):
        ui.notification_remove("abc")


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
