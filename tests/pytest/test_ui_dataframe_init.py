"""Tests for shiny/ui/dataframe/__init__.py - Dataframe module exports."""

from shiny.ui import dataframe


class TestDataframeExports:
    """Tests for dataframe module exports."""

    def test_output_data_frame_exported(self):
        """Test output_data_frame is exported."""
        assert hasattr(dataframe, "output_data_frame")
        assert callable(dataframe.output_data_frame)


class TestDataframeAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(dataframe.__all__, tuple)

    def test_all_contains_output_data_frame(self):
        """Test __all__ contains output_data_frame."""
        assert "output_data_frame" in dataframe.__all__
