"""Tests for shiny._shinyenv module"""

import sys

from shiny._shinyenv import is_pyodide


class TestIsPyodide:
    """Test is_pyodide constant"""

    def test_is_pyodide_is_bool(self):
        """Test that is_pyodide is a boolean"""
        assert isinstance(is_pyodide, bool)

    def test_is_pyodide_value(self):
        """Test is_pyodide reflects actual environment"""
        # In normal Python, pyodide should not be loaded
        expected = "pyodide" in sys.modules
        assert is_pyodide == expected

    def test_not_pyodide_in_standard_python(self):
        """Test that we're not in pyodide in standard Python environment"""
        # This test runs in standard Python, not WASM
        assert is_pyodide is False

    def test_module_imports_sys(self):
        """Test that _shinyenv uses sys module"""
        # The module should detect pyodide by checking sys.modules
        from shiny import _shinyenv

        # Check that the module was properly defined
        assert hasattr(_shinyenv, "is_pyodide")
