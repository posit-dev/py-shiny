"""Tests for shiny._shinyenv module."""

from shiny._shinyenv import is_pyodide


class TestShinyEnv:
    """Tests for shiny environment detection."""

    def test_is_pyodide_is_bool(self):
        """Test is_pyodide is a boolean."""
        assert isinstance(is_pyodide, bool)

    def test_is_pyodide_false_in_cpython(self):
        """Test is_pyodide is False when running in CPython."""
        # In normal test environment, we're not in Pyodide
        assert is_pyodide is False
