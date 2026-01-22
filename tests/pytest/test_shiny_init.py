"""Tests for shiny/__init__.py module exports."""

import shiny


class TestShinyExports:
    """Tests for shiny module exports."""

    def test_shiny_has_app(self):
        """Test shiny has App."""
        assert hasattr(shiny, "App")

    def test_shiny_has_module(self):
        """Test shiny has module."""
        assert hasattr(shiny, "module")

    def test_shiny_has_ui(self):
        """Test shiny has ui."""
        assert hasattr(shiny, "ui")

    def test_shiny_has_render(self):
        """Test shiny has render."""
        assert hasattr(shiny, "render")

    def test_shiny_has_reactive(self):
        """Test shiny has reactive."""
        assert hasattr(shiny, "reactive")


class TestShinyAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(shiny.__all__, tuple)

    def test_all_contains_app(self):
        """Test __all__ contains App."""
        assert "App" in shiny.__all__

    def test_all_contains_module(self):
        """Test __all__ contains module."""
        assert "module" in shiny.__all__

    def test_all_contains_ui(self):
        """Test __all__ contains ui."""
        assert "ui" in shiny.__all__

    def test_all_contains_render(self):
        """Test __all__ contains render."""
        assert "render" in shiny.__all__

    def test_all_contains_reactive(self):
        """Test __all__ contains reactive."""
        assert "reactive" in shiny.__all__
