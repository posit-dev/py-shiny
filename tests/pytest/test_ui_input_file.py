"""Tests for shiny/ui/_input_file.py - File input."""

from htmltools import Tag

from shiny.ui import input_file


class TestInputFile:
    """Tests for input_file function."""

    def test_input_file_returns_tag(self):
        """Test input_file returns a Tag."""
        result = input_file("file_id", "Upload a file")
        assert isinstance(result, Tag)

    def test_input_file_has_correct_id(self):
        """Test input_file has correct id."""
        result = input_file("file_id", "Upload a file")
        html = str(result)
        assert "file_id" in html

    def test_input_file_has_label(self):
        """Test input_file has label."""
        result = input_file("file_id", "Upload a file")
        html = str(result)
        assert "Upload a file" in html

    def test_input_file_single_by_default(self):
        """Test input_file is single file by default."""
        result = input_file("file_id", "Upload a file")
        html = str(result)
        # multiple attribute should not be present by default
        assert "multiple" not in html or 'multiple=""' not in html

    def test_input_file_multiple(self):
        """Test input_file with multiple=True."""
        result = input_file("file_id", "Upload a file", multiple=True)
        html = str(result)
        assert "multiple" in html

    def test_input_file_with_accept(self):
        """Test input_file with accept parameter."""
        result = input_file("file_id", "Upload", accept=".csv")
        html = str(result)
        assert ".csv" in html

    def test_input_file_with_accept_list(self):
        """Test input_file with accept list."""
        result = input_file("file_id", "Upload", accept=[".csv", ".txt"])
        html = str(result)
        assert ".csv" in html
        assert ".txt" in html

    def test_input_file_with_width(self):
        """Test input_file with width."""
        result = input_file("file_id", "Upload", width="400px")
        html = str(result)
        assert "400px" in html

    def test_input_file_button_label(self):
        """Test input_file with custom button label."""
        result = input_file("file_id", "Upload", button_label="Choose file")
        html = str(result)
        assert "Choose file" in html

    def test_input_file_default_button_label(self):
        """Test input_file has default button label."""
        result = input_file("file_id", "Upload")
        html = str(result)
        assert "Browse..." in html

    def test_input_file_placeholder(self):
        """Test input_file with custom placeholder."""
        result = input_file("file_id", "Upload", placeholder="Select a file...")
        html = str(result)
        assert "Select a file..." in html

    def test_input_file_default_placeholder(self):
        """Test input_file has default placeholder."""
        result = input_file("file_id", "Upload")
        html = str(result)
        assert "No file selected" in html

    def test_input_file_capture_environment(self):
        """Test input_file with capture=environment."""
        result = input_file("file_id", "Upload", capture="environment")
        html = str(result)
        assert "environment" in html

    def test_input_file_capture_user(self):
        """Test input_file with capture=user."""
        result = input_file("file_id", "Upload", capture="user")
        html = str(result)
        assert "user" in html


class TestInputFileAll:
    """Tests for __all__ exports."""

    def test_input_file_in_all(self):
        """Test input_file is in __all__."""
        from shiny.ui._input_file import __all__

        assert "input_file" in __all__
