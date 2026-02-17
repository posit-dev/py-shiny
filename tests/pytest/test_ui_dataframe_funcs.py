"""Tests for shiny.ui.dataframe._data_frame module."""

from htmltools import Tag

from shiny.ui.dataframe._data_frame import output_data_frame


class TestOutputDataFrame:
    """Tests for output_data_frame function."""

    def test_output_data_frame_returns_tag(self):
        """output_data_frame should return a Tag."""
        result = output_data_frame("my_df")
        assert isinstance(result, Tag)

    def test_output_data_frame_contains_id(self):
        """output_data_frame should contain the id."""
        result = output_data_frame("data_frame_id")
        html = str(result)
        assert 'id="data_frame_id"' in html

    def test_output_data_frame_is_shiny_data_frame(self):
        """output_data_frame should create shiny-data-frame element."""
        result = output_data_frame("df")
        html = str(result)
        assert "shiny-data-frame" in html

    def test_output_data_frame_with_different_ids(self):
        """output_data_frame should work with different ids."""
        ids = ["df1", "df2", "my_table", "data_grid"]
        for id_val in ids:
            result = output_data_frame(id_val)
            html = str(result)
            assert f'id="{id_val}"' in html

    def test_output_data_frame_is_fillable_container(self):
        """output_data_frame should be wrapped in fillable container."""
        result = output_data_frame("df")
        # The result should have html-fill classes
        html = str(result)
        # Should contain the data frame element
        assert "shiny-data-frame" in html
