"""Tests for shiny.ui._input_file module."""

from shiny.ui import input_file


class TestInputFile:
    """Tests for input_file function."""

    def test_input_file_basic(self):
        """Test basic input_file creation."""
        widget = input_file("file_id", "Upload File")
        html = str(widget)
        assert "file_id" in html
        assert "Upload File" in html

    def test_input_file_multiple(self):
        """Test input_file with multiple uploads."""
        widget = input_file("file_id", "Upload Files", multiple=True)
        html = str(widget)
        assert "multiple" in html

    def test_input_file_single(self):
        """Test input_file without multiple (default)."""
        widget = input_file("file_id", "Upload File", multiple=False)
        html = str(widget)
        assert "file_id" in html

    def test_input_file_with_accept_string(self):
        """Test input_file with accept as string."""
        widget = input_file("file_id", "Upload", accept=".csv")
        html = str(widget)
        assert ".csv" in html

    def test_input_file_with_accept_list(self):
        """Test input_file with accept as list."""
        widget = input_file("file_id", "Upload", accept=[".csv", ".xlsx"])
        html = str(widget)
        assert ".csv" in html
        assert ".xlsx" in html

    def test_input_file_with_accept_mime(self):
        """Test input_file with MIME type accept."""
        widget = input_file("file_id", "Upload", accept="text/plain")
        html = str(widget)
        assert "text/plain" in html

    def test_input_file_with_accept_image(self):
        """Test input_file with image/* accept."""
        widget = input_file("file_id", "Upload", accept="image/*")
        html = str(widget)
        assert "image/*" in html

    def test_input_file_with_width(self):
        """Test input_file with width."""
        widget = input_file("file_id", "Upload", width="300px")
        html = str(widget)
        assert "300px" in html

    def test_input_file_with_button_label(self):
        """Test input_file with custom button label."""
        widget = input_file("file_id", "Upload", button_label="Choose File")
        html = str(widget)
        assert "Choose File" in html

    def test_input_file_with_placeholder(self):
        """Test input_file with custom placeholder."""
        widget = input_file("file_id", "Upload", placeholder="Select a file...")
        html = str(widget)
        assert "Select a file..." in html

    def test_input_file_with_capture_environment(self):
        """Test input_file with capture for rear camera."""
        widget = input_file("file_id", "Upload", capture="environment")
        html = str(widget)
        assert "environment" in html

    def test_input_file_with_capture_user(self):
        """Test input_file with capture for front camera."""
        widget = input_file("file_id", "Upload", capture="user")
        html = str(widget)
        assert "user" in html

    def test_input_file_class(self):
        """Test input_file has correct CSS classes."""
        widget = input_file("file_id", "Upload")
        html = str(widget)
        assert "shiny-input-container" in html
