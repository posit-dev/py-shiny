"""Tests for shiny.bookmark._bookmark core behaviors."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from shiny import App, ui
from shiny._connection import MockConnection
from shiny.bookmark._bookmark import BookmarkApp, BookmarkExpressStub
from shiny.bookmark._save_state import BookmarkState
from shiny.session._session import AppSession


def test_bookmark_express_stub_no_ops() -> None:
    from shiny.express._stub_session import ExpressStubSession

    stub = ExpressStubSession()
    bookmark = BookmarkExpressStub(stub)

    assert bookmark.store == "disable"
    assert bookmark._restore_context is None
    assert asyncio.run(bookmark.get_bookmark_url()) is None
    asyncio.run(bookmark.do_bookmark())

    cancel = bookmark.on_bookmark(lambda state: None)
    cancel()


def test_bookmark_app_get_bookmark_url(monkeypatch: pytest.MonkeyPatch) -> None:
    app = App(ui.page_fluid(), lambda i, o, s: None, bookmark_store="url")
    session = AppSession(app, "id", MockConnection())
    bookmark = BookmarkApp(session)

    monkeypatch.setattr(BookmarkState, "_encode_state", lambda self: "qs")

    session.clientdata.url_protocol = lambda: "http:"
    session.clientdata.url_hostname = lambda: "example.com"
    session.clientdata.url_port = lambda: ""
    session.clientdata.url_pathname = lambda: "/app"

    url = asyncio.run(bookmark.get_bookmark_url())
    assert url == "http://example.com/app?qs"


def test_bookmark_app_update_query_string_invalid_mode() -> None:
    app = App(ui.page_fluid(), lambda i, o, s: None, bookmark_store="url")
    session = AppSession(app, "id", MockConnection())
    bookmark = BookmarkApp(session)

    with pytest.raises(ValueError, match="Invalid mode"):
        asyncio.run(bookmark.update_query_string("qs", mode="bad"))
