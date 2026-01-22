"""Tests for shiny.module module."""

import pytest

from shiny.module import current_namespace, resolve_id


class TestModule:
    """Tests for module functions."""

    def test_current_namespace_default(self) -> None:
        """Test current_namespace returns empty string by default."""
        result = current_namespace()
        assert result == ""

    def test_resolve_id_no_namespace(self) -> None:
        """Test resolve_id with no namespace."""
        result = resolve_id("my_input")
        assert str(result) == "my_input"

    def test_resolve_id_returns_resolved_id(self) -> None:
        """Test resolve_id returns a ResolvedId."""
        from shiny._namespaces import ResolvedId

        result = resolve_id("test")
        assert isinstance(result, ResolvedId)

    def test_resolve_id_validates(self) -> None:
        """Test resolve_id validates the id."""
        # Valid IDs should work
        resolve_id("valid_id")
        resolve_id("id123")

    def test_resolve_id_invalid_raises(self) -> None:
        """Test resolve_id raises for invalid id."""
        with pytest.raises(ValueError):
            resolve_id("")

        with pytest.raises(ValueError):
            resolve_id("invalid-id")
