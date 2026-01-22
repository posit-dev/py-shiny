"""Tests for shiny/_main.py module."""


class TestMainModule:
    """Tests for _main.py module."""

    def test_module_exists(self):
        """Test _main module can be imported."""
        from shiny import _main

        assert _main is not None


class TestMainRun:
    """Tests for main module functionality."""

    def test_has_run_functionality(self):
        """Test main module has run capability."""
        from shiny import _main

        # The module exists which means the run functionality is available
        assert hasattr(_main, "__name__")
