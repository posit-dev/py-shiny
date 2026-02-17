"""Tests for shiny._static module."""

from pathlib import Path

from shiny._static import get_default_shinylive_dir


class TestStaticModule:
    """Tests for static module functions."""

    def test_get_default_shinylive_dir_returns_path(self) -> None:
        """Test get_default_shinylive_dir returns Path."""
        result = get_default_shinylive_dir()
        assert isinstance(result, Path)

    def test_get_default_shinylive_dir_contains_shinylive(self) -> None:
        """Test get_default_shinylive_dir path contains 'shinylive'."""
        result = get_default_shinylive_dir()
        assert "shinylive" in str(result).lower()
