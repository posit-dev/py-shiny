"""Tests for shiny.ui._input_file module."""

from htmltools import Tag

from shiny.ui._input_file import input_file


class TestInputFile:
    """Tests for input_file function."""

    def test_input_file_basic(self) -> None:
        """Test basic input_file creation."""
        result = input_file("my_file", "Upload file:")
        assert isinstance(result, Tag)

    def test_input_file_has_id(self) -> None:
        """Test input_file has correct id."""
        result = input_file("file_id", "Label")
        html = str(result)
        assert "file_id" in html

    def test_input_file_with_label(self) -> None:
        """Test input_file with label."""
        result = input_file("file", "Choose a file:")
        html = str(result)
        assert "Choose a file:" in html

    def test_input_file_multiple(self) -> None:
        """Test input_file with multiple=True."""
        result = input_file("file", "Label", multiple=True)
        html = str(result)
        assert "multiple" in html

    def test_input_file_multiple_false(self) -> None:
        """Test input_file with multiple=False."""
        result = input_file("file", "Label", multiple=False)
        html = str(result)
        assert "file" in html

    def test_input_file_with_accept(self) -> None:
        """Test input_file with accept parameter."""
        result = input_file("file", "Label", accept=".csv")
        html = str(result)
        assert "accept" in html

    def test_input_file_with_accept_list(self) -> None:
        """Test input_file with accept as list."""
        result = input_file("file", "Label", accept=[".csv", ".txt"])
        html = str(result)
        assert "accept" in html

    def test_input_file_with_accept_mimetypes(self) -> None:
        """Test input_file with accept as mimetypes."""
        result = input_file("file", "Label", accept=["image/*", "application/pdf"])
        html = str(result)
        assert "accept" in html

    def test_input_file_with_width(self) -> None:
        """Test input_file with width parameter."""
        result = input_file("file", "Label", width="300px")
        html = str(result)
        assert "file" in html

    def test_input_file_with_button_label(self) -> None:
        """Test input_file with button_label parameter."""
        result = input_file("file", "Label", button_label="Browse...")
        html = str(result)
        assert "Browse..." in html

    def test_input_file_with_placeholder(self) -> None:
        """Test input_file with placeholder parameter."""
        result = input_file("file", "Label", placeholder="No file selected")
        html = str(result)
        assert "No file selected" in html
