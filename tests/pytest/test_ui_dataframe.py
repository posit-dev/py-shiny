"""Tests for shiny/ui/dataframe/_data_frame.py module."""

from shiny.ui.dataframe._data_frame import (
    output_data_frame,
)


class TestOutputDataFrame:
    """Tests for output_data_frame function."""

    def test_output_data_frame_is_callable(self):
        """Test output_data_frame is callable."""
        assert callable(output_data_frame)

    def test_output_data_frame_returns_tag(self):
        """Test output_data_frame returns a Tag."""
        from htmltools import Tag

        result = output_data_frame("my_df")
        assert isinstance(result, Tag)


class TestDataFrameExported:
    """Tests for data frame output functions export."""

    def test_output_data_frame_in_ui(self):
        """Test output_data_frame is in ui module."""
        from shiny import ui

        assert hasattr(ui, "output_data_frame")
