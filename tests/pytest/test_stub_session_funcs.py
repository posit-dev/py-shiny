"""Tests for shiny.express._stub_session module"""

import pytest
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from shiny._namespaces import Root
from shiny.express._stub_session import ExpressStubSession
from shiny.module import ResolvedId
from shiny.session import Inputs, Outputs


class TestExpressStubSession:
    """Test ExpressStubSession class"""

    def test_create_stub_session(self):
        """Test creating an ExpressStubSession"""
        session = ExpressStubSession()
        assert session is not None

    def test_stub_session_id(self):
        """Test stub session has expected id"""
        session = ExpressStubSession()
        assert session.id == "express_stub_session"

    def test_stub_session_has_input(self):
        """Test stub session has input object"""
        session = ExpressStubSession()
        assert isinstance(session.input, Inputs)

    def test_stub_session_has_output(self):
        """Test stub session has output object"""
        session = ExpressStubSession()
        assert isinstance(session.output, Outputs)

    def test_stub_session_ns_default(self):
        """Test stub session has default namespace"""
        session = ExpressStubSession()
        assert session.ns == Root

    def test_stub_session_ns_custom(self):
        """Test stub session with custom namespace"""
        ns = ResolvedId("custom_ns")
        session = ExpressStubSession(ns=ns)
        assert session.ns == ns

    def test_is_stub_session(self):
        """Test is_stub_session returns True"""
        session = ExpressStubSession()
        assert session.is_stub_session() is True

    def test_app_is_none(self):
        """Test stub session app is None"""
        session = ExpressStubSession()
        assert session.app is None

    def test_app_opts_empty(self):
        """Test app_opts starts empty"""
        session = ExpressStubSession()
        assert session.app_opts == {}


class TestExpressStubSessionMethods:
    """Test ExpressStubSession methods"""

    @pytest.mark.asyncio
    async def test_close_async(self):
        """Test async close method"""
        session = ExpressStubSession()
        # Should not raise
        await session.close()

    def test_is_hidden(self):
        """Test _is_hidden returns False"""
        session = ExpressStubSession()
        assert session._is_hidden("any_name") is False

    def test_on_ended(self):
        """Test on_ended returns callable"""
        session = ExpressStubSession()

        def callback():
            pass

        result = session.on_ended(callback)
        assert callable(result)

    def test_make_scope(self):
        """Test make_scope creates SessionProxy"""
        from shiny.session._session import SessionProxy

        session = ExpressStubSession()
        child = session.make_scope("child")
        assert isinstance(child, SessionProxy)

    def test_root_scope(self):
        """Test root_scope returns self"""
        session = ExpressStubSession()
        assert session.root_scope() is session

    def test_process_ui(self):
        """Test _process_ui returns empty deps"""
        session = ExpressStubSession()
        result = session._process_ui("test")
        assert result == {"deps": [], "html": ""}

    def test_send_input_message(self):
        """Test send_input_message does nothing"""
        session = ExpressStubSession()
        # Should not raise
        session.send_input_message("id", {"key": "value"})

    def test_send_insert_ui(self):
        """Test _send_insert_ui does nothing"""
        session = ExpressStubSession()
        # Should not raise
        session._send_insert_ui(
            "#selector", False, "beforeEnd", {"deps": [], "html": ""}
        )

    def test_send_remove_ui(self):
        """Test _send_remove_ui does nothing"""
        session = ExpressStubSession()
        # Should not raise
        session._send_remove_ui("#selector", False)

    def test_send_progress(self):
        """Test _send_progress does nothing"""
        session = ExpressStubSession()
        # Should not raise
        session._send_progress("type", {"message": "test"})

    @pytest.mark.asyncio
    async def test_send_custom_message(self):
        """Test send_custom_message does nothing"""
        session = ExpressStubSession()
        # Should not raise
        await session.send_custom_message("type", {"data": "test"})

    def test_set_message_handler(self):
        """Test set_message_handler returns empty string"""
        session = ExpressStubSession()

        def handler() -> str:
            return "ok"

        result = session.set_message_handler("name", handler)
        assert result == ""

    @pytest.mark.asyncio
    async def test_send_message_async(self):
        """Test _send_message does nothing"""
        session = ExpressStubSession()
        # Should not raise
        await session._send_message({"key": "value"})

    def test_send_message_sync(self):
        """Test _send_message_sync does nothing"""
        session = ExpressStubSession()
        # Should not raise
        session._send_message_sync({"key": "value"})

    def test_increment_busy_count(self):
        """Test _increment_busy_count does nothing"""
        session = ExpressStubSession()
        # Should not raise
        session._increment_busy_count()

    def test_decrement_busy_count(self):
        """Test _decrement_busy_count does nothing"""
        session = ExpressStubSession()
        # Should not raise
        session._decrement_busy_count()

    def test_on_flush(self):
        """Test on_flush returns callable"""
        session = ExpressStubSession()

        def callback():
            pass

        result = session.on_flush(callback)
        assert callable(result)

    def test_on_flushed(self):
        """Test on_flushed returns callable"""
        session = ExpressStubSession()

        def callback():
            pass

        result = session.on_flushed(callback)
        assert callable(result)

    def test_dynamic_route(self):
        """Test dynamic_route returns empty string"""
        session = ExpressStubSession()

        def handler(request: Request) -> PlainTextResponse:
            return PlainTextResponse("ok")

        result = session.dynamic_route("name", handler)
        assert result == ""

    @pytest.mark.asyncio
    async def test_unhandled_error(self):
        """Test _unhandled_error does nothing"""
        session = ExpressStubSession()
        # Should not raise
        await session._unhandled_error(Exception("test"))

    def test_download_returns_callable(self):
        """Test download returns a decorator"""
        session = ExpressStubSession()
        decorator = session.download()
        assert callable(decorator)

    def test_download_decorator_does_nothing(self):
        """Test download decorator returns None"""
        session = ExpressStubSession()
        decorator = session.download(id="dl")

        @decorator
        def download_handler():
            return [b"data"]

        # Decorator should not raise and should not modify the function significantly
