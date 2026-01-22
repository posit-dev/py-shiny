"""Tests for shiny._connection module."""

import pytest
from shiny._connection import MockConnection, ConnectionClosed


class TestMockConnection:
    """Tests for MockConnection class."""

    def test_mock_connection_creation(self):
        """Test creating a MockConnection."""
        conn = MockConnection()
        assert conn is not None

    def test_mock_connection_get_http_conn(self):
        """Test getting HTTP connection."""
        conn = MockConnection()
        http_conn = conn.get_http_conn()
        assert http_conn is not None
        assert http_conn.scope["type"] == "websocket"

    @pytest.mark.asyncio
    async def test_mock_connection_send(self):
        """Test send method (no-op in mock)."""
        conn = MockConnection()
        await conn.send("test message")  # Should not raise

    @pytest.mark.asyncio
    async def test_mock_connection_close(self):
        """Test close method (no-op in mock)."""
        conn = MockConnection()
        await conn.close(1000, "Normal closure")  # Should not raise

    @pytest.mark.asyncio
    async def test_mock_connection_receive(self):
        """Test receive method with cause_receive."""
        conn = MockConnection()
        conn.cause_receive("test message")
        result = await conn.receive()
        assert result == "test message"

    @pytest.mark.asyncio
    async def test_mock_connection_cause_disconnect(self):
        """Test cause_disconnect raises ConnectionClosed."""
        conn = MockConnection()
        conn.cause_disconnect()
        with pytest.raises(ConnectionClosed):
            await conn.receive()


class TestConnectionClosed:
    """Tests for ConnectionClosed exception."""

    def test_connection_closed_is_exception(self):
        """Test ConnectionClosed is an Exception."""
        assert issubclass(ConnectionClosed, Exception)

    def test_connection_closed_can_be_raised(self):
        """Test ConnectionClosed can be raised."""
        with pytest.raises(ConnectionClosed):
            raise ConnectionClosed()

    def test_connection_closed_with_message(self):
        """Test ConnectionClosed with message."""
        try:
            raise ConnectionClosed("Connection was closed")
        except ConnectionClosed as e:
            assert "Connection was closed" in str(e)
