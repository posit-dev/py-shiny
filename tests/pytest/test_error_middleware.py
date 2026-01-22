"""Tests for the _error module."""

from typing import Any, MutableMapping

import pytest
from starlette.types import Message, Receive, Scope, Send

from shiny._error import ErrorMiddleware


class TestErrorMiddleware:
    """Tests for the ErrorMiddleware class."""

    def test_error_middleware_init(self):
        """Test ErrorMiddleware initialization."""

        async def mock_app(scope: Scope, receive: Receive, send: Send) -> None:
            pass

        middleware = ErrorMiddleware(mock_app)
        assert middleware.app is mock_app

    @pytest.mark.asyncio
    async def test_error_middleware_passes_through(self):
        """Test that ErrorMiddleware passes through successful requests."""
        called = False

        async def mock_app(scope: Scope, receive: Receive, send: Send) -> None:
            nonlocal called
            called = True

        async def mock_receive() -> Message:
            return {"type": "http.request", "body": b""}

        async def mock_send(message: Message) -> None:
            pass

        middleware = ErrorMiddleware(mock_app)
        await middleware({"type": "http"}, mock_receive, mock_send)

        assert called is True

    @pytest.mark.asyncio
    async def test_error_middleware_handles_http_exception(self):
        """Test that ErrorMiddleware handles HTTPException."""
        import starlette.exceptions as exceptions

        async def mock_app(scope: Scope, receive: Receive, send: Send) -> None:
            raise exceptions.HTTPException(status_code=404, detail="Not Found")

        middleware = ErrorMiddleware(mock_app)

        responses: list[MutableMapping[str, Any]] = []

        async def mock_receive() -> Message:
            return {"type": "http.request", "body": b""}

        async def mock_send(message: Message) -> None:
            responses.append(message)

        scope: Scope = {"type": "http"}  # type: ignore[typeddict-item]

        await middleware(scope, mock_receive, mock_send)

        # Should have sent a response
        assert len(responses) > 0
        # First message should be http.response.start
        assert responses[0]["type"] == "http.response.start"
        assert responses[0]["status"] == 404

    @pytest.mark.asyncio
    async def test_error_middleware_handles_generic_exception(self):
        """Test that ErrorMiddleware handles generic exceptions."""

        async def mock_app(scope: Scope, receive: Receive, send: Send) -> None:
            raise ValueError("Something went wrong")

        middleware = ErrorMiddleware(mock_app)

        responses: list[MutableMapping[str, Any]] = []

        async def mock_receive() -> Message:
            return {"type": "http.request", "body": b""}

        async def mock_send(message: Message) -> None:
            responses.append(message)

        scope: Scope = {"type": "http"}  # type: ignore[typeddict-item]

        await middleware(scope, mock_receive, mock_send)

        # Should have sent a 500 response
        assert len(responses) > 0
        assert responses[0]["type"] == "http.response.start"
        assert responses[0]["status"] == 500
