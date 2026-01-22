"""Tests for shiny/run/__init__.py - Run module exports."""

from shiny import run


class TestRunExports:
    """Tests for run module exports."""

    def test_run_shiny_app_exported(self):
        """Test run_shiny_app is exported."""
        assert hasattr(run, "run_shiny_app")
        assert callable(run.run_shiny_app)

    def test_shinyappproc_exported(self):
        """Test ShinyAppProc is exported."""
        assert hasattr(run, "ShinyAppProc")


class TestRunAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(run.__all__, tuple)

    def test_all_contains_run_shiny_app(self):
        """Test __all__ contains run_shiny_app."""
        assert "run_shiny_app" in run.__all__

    def test_all_contains_shinyappproc(self):
        """Test __all__ contains ShinyAppProc."""
        assert "ShinyAppProc" in run.__all__
