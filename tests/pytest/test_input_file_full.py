"""Tests for shiny/ui/_input_file.py module."""

from shiny.ui._input_file import input_file


class TestInputFile:
    """Tests for input_file function."""

    def test_input_file_is_callable(self):
        """Test input_file is callable."""
        assert callable(input_file)

    def test_input_file_returns_tag(self):
        """Test input_file returns a Tag."""
        from htmltools import Tag

        result = input_file("my_file", "Upload file")
        assert isinstance(result, Tag)

    def test_input_file_with_accept(self):
        """Test input_file with accept parameter."""
        from htmltools import Tag

        result = input_file("my_file", "Upload file", accept=[".csv", ".txt"])
        assert isinstance(result, Tag)

    def test_input_file_with_multiple(self):
        """Test input_file with multiple parameter."""
        from htmltools import Tag

        result = input_file("my_file", "Upload files", multiple=True)
        assert isinstance(result, Tag)


class TestInputFileExported:
    """Tests for file input functions export."""

    def test_input_file_in_ui(self):
        """Test input_file is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_file")
