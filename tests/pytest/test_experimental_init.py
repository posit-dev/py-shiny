"""Tests for shiny/experimental/__init__.py module."""

import shiny.experimental as experimental


class TestExperimentalExports:
    """Tests for experimental module exports."""

    def test_experimental_has_ui(self):
        """Test experimental has ui submodule."""
        assert hasattr(experimental, "ui")


class TestExperimentalAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(experimental.__all__, tuple)

    def test_all_contains_ui(self):
        """Test __all__ contains ui."""
        assert "ui" in experimental.__all__
