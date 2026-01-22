"""Tests for shiny/_utils.py module."""

from shiny._utils import (
    rand_hex,
    drop_none,
)


class TestRandHex:
    """Tests for rand_hex function."""

    def test_rand_hex_is_callable(self):
        """Test rand_hex is callable."""
        assert callable(rand_hex)

    def test_rand_hex_returns_string(self):
        """Test rand_hex returns a string."""
        result = rand_hex(8)
        assert isinstance(result, str)

    def test_rand_hex_length(self):
        """Test rand_hex returns correct length (actually returns 2*bytes)."""
        result = rand_hex(8)
        # rand_hex(n) returns 2*n characters (hex encoding)
        assert len(result) == 16


class TestDropNone:
    """Tests for drop_none function."""

    def test_drop_none_is_callable(self):
        """Test drop_none is callable."""
        assert callable(drop_none)

    def test_drop_none_removes_none_values(self):
        """Test drop_none removes None values."""
        result = drop_none({"a": 1, "b": None, "c": 3})
        assert result == {"a": 1, "c": 3}
